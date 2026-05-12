"""Execution result for agent operations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class ToolCallRecord:
    tool_name: str
    arguments: dict
    result: Any
    latency_ms: int = 0
    success: bool = True


@dataclass
class ExecutionResult:
    """Standardized result from agent execution."""

    content: str
    reasoning: str = ""
    steps_taken: int = 0
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    usage: dict = field(default_factory=dict)  # tokens, cost, latency
    skills_used: list[str] = field(default_factory=list)
    skills_distilled: list[str] = field(default_factory=list)
    error: Optional[str] = None
    completed_at: datetime = field(default_factory=datetime.now)

    @property
    def is_success(self) -> bool:
        return self.error is None
