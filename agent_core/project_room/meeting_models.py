"""
Meeting Models - 会议数据模型
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Round:
    """一轮讨论发言"""
    round_number: int
    author: str
    content: str
    type: str = "discussion"
    timestamp: float = 0.0
    thinking_content: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().timestamp()

    def to_dict(self) -> dict:
        d = asdict(self)
        if not d.get("thinking_content"):
            d.pop("thinking_content", None)
        return d


@dataclass
class MeetingSession:
    """一个会议房间的完整状�?""
    room_id: str
    topic: str
    agents: list
    status: str = "discussing"
    rounds: list = field(default_factory=list)
    consensus: bool = False
    consensus_reason: str = ""
    artifacts: dict = field(default_factory=dict)
    parent_room: str = ""

    def to_dict(self) -> dict:
        return {
            "room_id": self.room_id,
            "topic": self.topic,
            "agents": self.agents,
            "status": self.status,
            "rounds": [r.to_dict() for r in self.rounds],
            "consensus": self.consensus,
            "consensus_reason": self.consensus_reason,
            "artifacts": self.artifacts,
            "parent_room": self.parent_room,
        }

    @property
    def current_round(self) -> int:
        return len(self.rounds) + 1

    def next_speaker(self) -> str:
        """
        确定下一轮谁发言�?        规则�?          - Round 1: 列表第一�?Agent 先提方案
          - 后续�?iris �?agents 轮流补充
          - 所有人说完后，iris 评审
          - 如果还有分歧，回到第一�?Agent 继续
        """
        round_num = self.current_round

        if round_num == 1:
            return self.agents[0] if self.agents else "iris"

        sequence = list(self.agents) + ["iris"]
        sequence_len = len(sequence)

        pos = (round_num - 1) % sequence_len
        return sequence[pos]