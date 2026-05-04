"""
Meeting Discussion - Meeting discussion management
"""

from typing import Dict, List, Any


class DiscussionRound:
    """Discussion round in a meeting"""

    def __init__(self, round_number: int, author: str, content: str):
        self.round_number = round_number
        self.author = author
        self.content = content


class Discussion:
    """Meeting discussion manager"""

    def __init__(self, meeting_id: str):
        self.meeting_id = meeting_id
        self.rounds: List[DiscussionRound] = []

    def add_round(self, round_number: int, author: str, content: str) -> int:
        """Add a discussion round"""
        round_obj = DiscussionRound(round_number, author, content)
        self.rounds.append(round_obj)
        return len(self.rounds)

    def get_rounds(self) -> List[Dict[str, Any]]:
        """Get all discussion rounds"""
        return [
            {
                "round_number": r.round_number,
                "author": r.author,
                "content": r.content,
            }
            for r in self.rounds
        ]


discussions: Dict[str, Discussion] = {}


def get_discussion(meeting_id: str) -> Discussion:
    """Get or create discussion for meeting"""
    if meeting_id not in discussions:
        discussions[meeting_id] = Discussion(meeting_id)
    return discussions[meeting_id]


def _get_agent_name(agent_id: str) -> str:
    """Get agent display name from ID"""
    # Simple mapping - would normally look up from agent manager
    name_map = {
        'iris': 'I.R.I.S.',
        'coder': 'Code Assistant',
        'researcher': 'Research Assistant',
    }
    return name_map.get(agent_id, agent_id)


def _write_to_whiteboard(meeting_id: str, content: str, author: str = '') -> bool:
    """Write content to meeting whiteboard"""
    # Would normally interact with whiteboard system
    return True
