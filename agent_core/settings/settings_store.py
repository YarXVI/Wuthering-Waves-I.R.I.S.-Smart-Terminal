"""
Settings Store - Persistent Settings Management
JSON file storage with hot-reload support
"""
import json
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from dotenv import load_dotenv
from agent_core.utils.filelock import locked_write, locked_read
from agent_core.utils.text import mask_api_keys_in_dict

# Load .env if not already loaded
load_dotenv()

# Read defaults from environment variables
_DEFAULT_API_KEY = os.getenv("OPENAI_API_KEY", "")
_DEFAULT_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
_DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Settings file paths
SETTINGS_DIR = Path(__file__).parent.parent.parent / "config"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"


@dataclass
class ProviderConfig:
    """API Provider Configuration"""
    id: str = ""                         # Unique identifier
    name: str = ""                       # Display name
    api_type: str = "openai"             # openai / anthropic / ollama / custom
    api_key: str = ""
    base_url: str = ""
    model: str = "gpt-4o"
    is_active: bool = False

    def resolved_api_key(self) -> str:
        """
        Resolve api_key:
        - If value starts with $, treat as environment variable reference
        - Otherwise return original value
        """
        key = self.api_key
        if key.startswith("$"):
            env_name = key[1:].strip()
            return os.environ.get(env_name, "")
        return key


@dataclass
class MCPConfig:
    """MCP Server Configuration"""
    id: str = ""
    name: str = ""
    command: str = ""                     # Startup command
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    enabled: bool = False


@dataclass
class SkillBinding:
    """Skill to Agent Binding"""
    skill_name: str = ""
    agent_id: str = ""
    enabled: bool = True


@dataclass
class AgentSettings:
    """Agent Personalized Settings"""
    id: str = ""
    provider_id: str = ""                 # Provider to use
    system_prompt_override: str = ""
    temperature: float = 0.3
    top_k_memories: int = 3


@dataclass
class AppSettings:
    """Global Application Settings"""
    # Version
    version: int = 1

    # API Providers
    providers: list[ProviderConfig] = field(default_factory=lambda: [
        ProviderConfig(
            id="default",
            name="Default (from .env)",
            api_type="openai",
            api_key=_DEFAULT_API_KEY,
            base_url=_DEFAULT_BASE_URL,
            model=_DEFAULT_MODEL,
            is_active=True,
        ),
        ProviderConfig(
            id="openai",
            name="OpenAI",
            api_type="openai",
            api_key=_DEFAULT_API_KEY,
            base_url=_DEFAULT_BASE_URL,
            model=_DEFAULT_MODEL,
            is_active=False,
        ),
    ])

    # MCP Servers
    mcp_servers: list[MCPConfig] = field(default_factory=list)

    # Skill Bindings
    skill_bindings: list[SkillBinding] = field(default_factory=list)

    # Agent Personalization
    agent_settings: list[AgentSettings] = field(default_factory=list)

    # General
    memrag_enabled: bool = False
    theme: str = "dark"


class SettingsStore:
    """Persistent Settings Storage"""

    def __init__(self):
        self._settings: AppSettings | None = None

    def load(self) -> AppSettings:
        """Load settings from disk"""
        if not SETTINGS_FILE.exists():
            self._settings = AppSettings()
            self.save()
            return self._settings
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._settings = self._from_dict(data)
            return self._settings
        except Exception:
            self._settings = AppSettings()
            return self._settings

    def save(self):
        """Save settings to disk (with file lock to prevent race conditions)"""
        if self._settings is None:
            return
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        data = self._to_dict(self._settings)
        # Backup before writing (prevent corruption)
        if SETTINGS_FILE.exists():
            backup = SETTINGS_FILE.with_suffix(".json.bak")
            try:
                os.replace(SETTINGS_FILE, backup)
            except OSError:
                pass
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if not locked_write(SETTINGS_FILE, json_str):
            # Fallback: use regular write
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                f.write(json_str)

    @property
    def settings(self) -> AppSettings:
        if self._settings is None:
            self.load()
        return self._settings

    def get_active_provider(self) -> ProviderConfig | None:
        """Get currently active API provider"""
        for p in self.settings.providers:
            if p.is_active:
                return p
        if self.settings.providers:
            return self.settings.providers[0]
        return None

    def get_agent_settings(self, agent_id: str) -> AgentSettings | None:
        """Get personalized settings for specified Agent"""
        for a in self.settings.agent_settings:
            if a.id == agent_id:
                return a
        return None

    def get_agent_provider(self, agent_id: str) -> ProviderConfig | None:
        """Get provider used by specified Agent (uses default if none specified)"""
        agent_set = self.get_agent_settings(agent_id)
        if agent_set and agent_set.provider_id:
            for p in self.settings.providers:
                if p.id == agent_set.provider_id:
                    return p
        return self.get_active_provider()

    def update_providers(self, providers: list[dict]):
        """Update API providers list"""
        self.settings.providers = [ProviderConfig(**p) for p in providers]
        self.save()

    def update_mcp_servers(self, servers: list[dict]):
        """Update MCP servers list"""
        self.settings.mcp_servers = [MCPConfig(**s) for s in servers]
        self.save()

    def update_agent_settings(self, agent_settings: list[dict]):
        """Update Agent settings"""
        self.settings.agent_settings = [AgentSettings(**a) for a in agent_settings]
        self.save()

    def to_dict(self) -> dict:
        """Export as dictionary (for internal persistence)"""
        return self._to_dict(self.settings)

    def to_dict_masked(self) -> dict:
        """Export as dictionary with masked API keys (for API responses)"""
        raw = self._to_dict(self.settings)
        return mask_api_keys_in_dict(raw)

    @staticmethod
    def _from_dict(data: dict) -> AppSettings:
        providers = [ProviderConfig(**p) for p in data.get("providers", [])]
        mcp = [MCPConfig(**s) for s in data.get("mcp_servers", [])]
        bindings = [SkillBinding(**b) for b in data.get("skill_bindings", [])]
        agent_set = [AgentSettings(**a) for a in data.get("agent_settings", [])]
        return AppSettings(
            version=data.get("version", 1),
            providers=providers,
            mcp_servers=mcp,
            skill_bindings=bindings,
            agent_settings=agent_set,
            memrag_enabled=data.get("memrag_enabled", False),
            theme=data.get("theme", "dark"),
        )

    @staticmethod
    def _to_dict(s: AppSettings) -> dict:
        return {
            "version": s.version,
            "providers": [asdict(p) for p in s.providers],
            "mcp_servers": [asdict(m) for m in s.mcp_servers],
            "skill_bindings": [asdict(b) for b in s.skill_bindings],
            "agent_settings": [asdict(a) for a in s.agent_settings],
            "memrag_enabled": s.memrag_enabled,
            "theme": s.theme,
        }


# Global singleton
settings_store = SettingsStore()
