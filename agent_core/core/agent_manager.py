"""
Agent Manager - Manages multiple virtual agent lifecycles
All external services (providers, MCP, skills) are loaded through isolation layer
"""

import threading
from agent_core.core.agent import Agent
from agent_core.core.agent_profile import (
    AgentProfile,
    AgentStatus,
    DEFAULT_AGENTS,
)
from agent_core.core.agent_store import load_agents, save_agents
from agent_core.utils.isolation import safe_import, safe_call

# ---- Isolated loading: service modules ----
_settings_store = safe_import("agent_core.settings.settings_store")
_settings_store_instance = getattr(_settings_store, "settings_store", None) if _settings_store else None

_providers_mod = safe_import("agent_core.providers")
_registry = getattr(_providers_mod, "registry", None) if _providers_mod else None

_mcp_mod = safe_import("agent_core.mcp.mcp_client")
_mcp_manager = getattr(_mcp_mod, "mcp_manager", None) if _mcp_mod else None

_skills_mod = safe_import("agent_core.skills_registry")
_skills_registry = getattr(_skills_mod, "skills_registry", None) if _skills_mod else None

# ---- Isolated loading: collaboration modules ----
_collab_orch = safe_import("agent_core.collaboration.orchestrator")
_orchestrator = getattr(_collab_orch, "orchestrator", None) if _collab_orch else None


class AgentManager:
    """Agent Manager - Any service module failure won't affect other functions"""

    def __init__(self):
        self.profiles: dict[str, AgentProfile] = {}
        self.runtimes: dict[str, Agent] = {}
        self._current_caller_id: str = ""
        self._lock = threading.RLock()
        self._init_defaults()

    def _init_defaults(self):
        """Initialize default Agent list, each service loads independently"""
        # Load API provider
        if _settings_store_instance:
            safe_call(_settings_store_instance.load, None)
        if _registry and _settings_store_instance:
            store = safe_call(lambda: _settings_store_instance.settings, None)
            if store:
                api_key = safe_call(lambda: getattr(store, 'openai_api_key', ''), None)
                if api_key:
                    _registry.register_provider("openai", {"api_key": api_key})

        # Load default agents from profile
        for agent_profile in DEFAULT_AGENTS:
            profile_id = agent_profile.get("id")
            if profile_id:
                self.profiles[profile_id] = agent_profile

        # Load saved agents from disk - load_agents returns dict[str, AgentProfile]
        saved_agents = safe_call(load_agents, {})
        if isinstance(saved_agents, dict):
            for agent_id, agent_data in saved_agents.items():
                if agent_id:
                    self.profiles[agent_id] = agent_data

    def create_agent(self, profile_id: str) -> bool:
        """Create agent runtime from profile"""
        with self._lock:
            if profile_id not in self.profiles:
                return False

            if profile_id in self.runtimes:
                return True

            profile = self.profiles[profile_id]
            agent = Agent(
                name=profile.name if hasattr(profile, 'name') else "Unnamed",
                model=profile.model if hasattr(profile, 'model') else "gpt-4o",
                api_key=profile.api_key if hasattr(profile, 'api_key') else None,
                system_prompt=profile.system_prompt if hasattr(profile, 'system_prompt') else "",
            )
            self.runtimes[profile_id] = agent
            return True

    def get_agent(self, profile_id: str) -> Agent:
        """Get agent runtime"""
        with self._lock:
            if profile_id not in self.runtimes:
                self.create_agent(profile_id)
            return self.runtimes.get(profile_id)

    def list_agents(self) -> list[dict]:
        """List all agent profiles"""
        return list(self.profiles.values())

    def get_agent_profile(self, profile_id: str) -> dict:
        """Get agent profile by ID"""
        return self.profiles.get(profile_id, {})

    def update_agent_profile(self, profile_id: str, updates: dict) -> bool:
        """Update agent profile"""
        with self._lock:
            if profile_id not in self.profiles:
                return False
            self.profiles[profile_id].update(updates)
            return True

    def delete_agent(self, profile_id: str) -> bool:
        """Delete agent"""
        with self._lock:
            if profile_id in self.profiles:
                del self.profiles[profile_id]
            if profile_id in self.runtimes:
                del self.runtimes[profile_id]
            return True


manager = AgentManager()
