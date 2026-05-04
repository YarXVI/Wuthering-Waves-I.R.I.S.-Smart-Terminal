"""
Agent Profile - Define agent configurations
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class AgentStatus(Enum):
    """Agent status enum"""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"


@dataclass
class AgentProfile:
    """Agent profile definition"""
    id: str
    name: str
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    system_prompt: str = ""
    status: str = "idle"
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "api_key": self.api_key,
            "system_prompt": self.system_prompt,
            "status": self.status,
            "description": self.description,
        }


DEFAULT_AGENTS = [
    {
        "id": "iris",
        "name": "I.R.I.S.",
        "model": "gpt-4o",
        "system_prompt": "You are I.R.I.S., an intelligent virtual office assistant.",
        "description": "Main virtual office assistant",
    },
    {
        "id": "coder",
        "name": "Code Assistant",
        "model": "gpt-4o",
        "system_prompt": "You are a coding assistant specializing in code review and debugging.",
        "description": "Helps with programming tasks",
    },
    {
        "id": "researcher",
        "name": "Research Assistant",
        "model": "gpt-4o",
        "system_prompt": "You are a research assistant specializing in information gathering and analysis.",
        "description": "Helps with research tasks",
    },
]
