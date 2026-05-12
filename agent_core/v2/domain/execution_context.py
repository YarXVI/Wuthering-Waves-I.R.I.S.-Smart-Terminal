"""Execution context for agent operations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass(frozen=True)
class ExecutionContext:
    """Immutable context passed through the entire execution pipeline."""

    agent_id: str
    user_id: str = "default"
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    room_id: Optional[str] = None
    task_type: str = "chat"  # chat, meeting, workflow, subagent
    priority: int = 5  # 1-10, higher = more important
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def with_metadata(self, **kwargs) -> "ExecutionContext":
        """Return a new context with updated metadata."""
        new_meta = dict(self.metadata)
        new_meta.update(kwargs)
        return ExecutionContext(
            agent_id=self.agent_id,
            user_id=self.user_id,
            session_id=self.session_id,
            room_id=self.room_id,
            task_type=self.task_type,
            priority=self.priority,
            metadata=new_meta,
            created_at=self.created_at,
        )
