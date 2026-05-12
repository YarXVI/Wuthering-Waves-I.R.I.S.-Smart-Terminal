"""Tiered memory manager."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class MemoryContext:
    """Aggregated memory context for an agent."""

    working: dict = field(default_factory=dict)
    short_term: list = field(default_factory=list)
    long_term: list = field(default_factory=list)
    user_profile: dict = field(default_factory=dict)


class MemoryManager:
    """Tiered memory manager."""

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path.home() / ".iris" / "memory"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._working: dict[str, dict] = {}  # agent_id -> working memory
        self._session_cache: dict[str, list] = {}  # session_id -> recent messages

    def _agent_dir(self, agent_id: str) -> Path:
        return self.storage_dir / agent_id

    async def load(self, agent_id: str, user_id: str = "default") -> MemoryContext:
        """Load all memory tiers."""
        agent_dir = self._agent_dir(agent_id)
        agent_dir.mkdir(parents=True, exist_ok=True)

        working = self._working.get(agent_id, {})
        short_term = await self._load_short_term(agent_id)
        long_term = await self._load_long_term(agent_id, user_id)
        user_profile = await self._load_user_profile(user_id)

        return MemoryContext(
            working=working,
            short_term=short_term,
            long_term=long_term,
            user_profile=user_profile,
        )

    async def save_message(self, agent_id: str, message: dict) -> None:
        """Save a message to short-term memory."""
        agent_dir = self._agent_dir(agent_id)
        agent_dir.mkdir(parents=True, exist_ok=True)
        history_file = agent_dir / "history.jsonl"

        entry = {
            **message,
            "timestamp": datetime.now().isoformat(),
        }
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    async def add_memory(self, agent_id: str, content: str, importance: int = 5) -> None:
        """Add a long-term memory."""
        agent_dir = self._agent_dir(agent_id)
        agent_dir.mkdir(parents=True, exist_ok=True)
        memory_file = agent_dir / "long_term.jsonl"

        entry = {
            "content": content,
            "importance": importance,
            "timestamp": datetime.now().isoformat(),
        }
        with open(memory_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    async def update_working_memory(self, agent_id: str, data: dict) -> None:
        """Update working memory (L1)."""
        if agent_id not in self._working:
            self._working[agent_id] = {}
        self._working[agent_id].update(data)

    async def _load_short_term(self, agent_id: str, limit: int = 20) -> list:
        """Load recent messages."""
        history_file = self._agent_dir(agent_id) / "history.jsonl"
        if not history_file.exists():
            return []

        lines = []
        with open(history_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        entries = [json.loads(line) for line in lines[-limit:] if line.strip()]
        return entries

    async def _load_long_term(self, agent_id: str, user_id: str, limit: int = 10) -> list:
        """Load long-term memories (simplified)."""
        memory_file = self._agent_dir(agent_id) / "long_term.jsonl"
        if not memory_file.exists():
            return []

        lines = []
        with open(memory_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        entries = [json.loads(line) for line in lines if line.strip()]
        entries.sort(key=lambda x: x.get("importance", 0), reverse=True)
        return entries[:limit]

    async def _load_user_profile(self, user_id: str) -> dict:
        """Load user profile."""
        profile_file = self.storage_dir / "profiles" / f"{user_id}.json"
        if not profile_file.exists():
            return {}
        with open(profile_file, "r", encoding="utf-8") as f:
            return json.load(f)
