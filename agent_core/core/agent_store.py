"""
Agent Store - Custom Agent configuration persistence
Uses JSON file storage, supports CRUD operations with graceful degradation
"""

import json
import os
import re
from pathlib import Path
from dataclasses import asdict
from typing import Optional

from agent_core.core.agent_profile import AgentProfile, DEFAULT_AGENTS
from agent_core.utils.filelock import locked_write

# Storage directory: memory/
MEMORY_DIR = Path(__file__).parent.parent.parent / "memory"
AGENTS_FILE = MEMORY_DIR / "agents.json"

# Field blacklist (runtime state, not persisted)
_SKIP_FIELDS = {"status", "current_task", "message_count"}


def _to_dict(profile: AgentProfile) -> dict:
    """Convert AgentProfile to serializable dict (excluding runtime state)"""
    d = asdict(profile)
    for skip in _SKIP_FIELDS:
        d.pop(skip, None)
    return d


def _from_dict(data: dict) -> AgentProfile:
    """Convert dict to AgentProfile"""
    return AgentProfile(
        id=data.get("id", ""),
        name=data.get("name", ""),
        model=data.get("model", "gpt-4o"),
        system_prompt=data.get("system_prompt", ""),
        description=data.get("description", ""),
    )


def _ensure_storage_dir():
    """Ensure storage directory exists"""
    try:
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError):
        return False


def load_agents() -> dict[str, AgentProfile]:
    """
    Load custom Agent list from disk
    Falls back to DEFAULT_AGENTS if file doesn't exist or is corrupted
    """
    # Ensure default set exists (memory fallback)
    # Convert DEFAULT_AGENTS list to dict with agent id as key
    agents = {agent["id"]: _from_dict(agent) for agent in DEFAULT_AGENTS}

    if not AGENTS_FILE.exists():
        return agents

    try:
        with open(AGENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return agents

        stored = data.get("agents", {})
        if not isinstance(stored, dict):
            return agents

        # Merge: prefer stored config, but ensure iris always exists
        merged = {agent["id"]: _from_dict(agent) for agent in DEFAULT_AGENTS}
        for aid, raw in stored.items():
            if not isinstance(raw, dict):
                continue
            # Inherit fields from default set (e.g., system_prompt)
            # Use defaults for missing fields in storage
            existing = merged.get(aid)
            if existing:
                for key in asdict(existing):
                    if key not in raw and key not in _SKIP_FIELDS:
                        raw[key] = getattr(existing, key, "")
            merged[aid] = _from_dict(raw)

        return merged

    except (json.JSONDecodeError, OSError, PermissionError, Exception):
        # Graceful degradation
        return agents


def save_agents(agents: dict[str, AgentProfile]) -> bool:
    """
    Persist Agent list to disk
    Fails gracefully without affecting main flow
    """
    if not _ensure_storage_dir():
        return False

    try:
        data = {"agents": {aid: _to_dict(p) for aid, p in agents.items()}}
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if not locked_write(AGENTS_FILE, json_str):
            # Fallback: normal write
            with open(AGENTS_FILE, "w", encoding="utf-8") as f:
                f.write(json_str)
        return True
    except (OSError, PermissionError, Exception):
        return False


def generate_agent_id(name: str) -> str:
    """Generate unique English ID from name (lowercase letters, underscores, Chinese)"""
    # Remove special characters, convert spaces to underscores, lowercase
    agent_id = re.sub(r"[^a-zA-Z0-9_\u4e00-\u9fff]", "", name.strip())
    agent_id = re.sub(r"\s+", "_", agent_id)
    agent_id = agent_id.lower()
    # Fallback for empty name
    if not agent_id:
        agent_id = "custom_agent"
    # Truncate
    return agent_id[:32]
