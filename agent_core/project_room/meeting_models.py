"""
Meeting Models - Meeting data models
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class MeetingRecord:
    """Meeting record"""
    meeting_id: str
    title: str
    created_at: str
    status: str = "active"


@dataclass
class Round:
    """Discussion round"""
    round_number: int
    author: str
    content: str
    timestamp: Optional[str] = None


@dataclass
class MeetingSession:
    """Meeting session"""
    room_id: str
    topic: str
    agents: List[str] = None
    status: str = "active"
    current_round: int = 0
    max_rounds: int = 6
    created_at: str = ""
    
    def __post_init__(self):
        if self.agents is None:
            self.agents = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
