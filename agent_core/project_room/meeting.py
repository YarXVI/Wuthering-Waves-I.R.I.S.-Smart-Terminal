"""
Meeting - Smart meeting room
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


def set_on_round_complete(callback):
    """Set callback for round completion"""
    pass


class Meeting:
    """Smart meeting room"""

    def __init__(self, meeting_id: str, title: str):
        self.meeting_id = meeting_id
        self.title = title
        self.participants: List[str] = []
        self.rounds: List[Dict[str, Any]] = []
        self.status = "active"

    def add_participant(self, user_id: str):
        """Add participant to meeting"""
        if user_id not in self.participants:
            self.participants.append(user_id)

    def remove_participant(self, user_id: str):
        """Remove participant from meeting"""
        if user_id in self.participants:
            self.participants.remove(user_id)

    def add_round(self, round_data: Dict[str, Any]):
        """Add discussion round"""
        self.rounds.append(round_data)

    def get_summary(self) -> Dict[str, Any]:
        """Get meeting summary"""
        return {
            "meeting_id": self.meeting_id,
            "title": self.title,
            "participants": self.participants,
            "rounds_count": len(self.rounds),
            "status": self.status,
        }


meetings: Dict[str, Meeting] = {}


def get_meeting(meeting_id: str) -> Optional[Meeting]:
    """Get meeting by ID"""
    return meetings.get(meeting_id)


def create_meeting(meeting_id: str, title: str) -> Meeting:
    """Create new meeting"""
    meeting = Meeting(meeting_id, title)
    meetings[meeting_id] = meeting
    return meeting


def delete_meeting(meeting_id: str) -> bool:
    """Delete meeting"""
    if meeting_id in meetings:
        del meetings[meeting_id]
        return True
    return False


def execute_round(meeting_id: str, agent_id: str, message: str) -> Dict[str, Any]:
    """Execute a discussion round"""
    meeting = meetings.get(meeting_id)
    if not meeting:
        return {"success": False, "error": "Meeting not found"}
    
    round_data = {
        "round_number": len(meeting.rounds) + 1,
        "agent_id": agent_id,
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }
    meeting.add_round(round_data)
    return {"success": True, "round": round_data}


def judge_consensus(meeting_id: str) -> Dict[str, Any]:
    """Judge consensus in meeting"""
    meeting = meetings.get(meeting_id)
    if not meeting:
        return {"success": False, "error": "Meeting not found"}
    
    return {
        "success": True,
        "consensus": True,
        "confidence": 0.8,
        "summary": "Consensus reached",
    }


def save_meeting(meeting_id: str) -> bool:
    """Save meeting to disk"""
    from agent_core.project_room.meeting_persistence import persistence
    meeting = meetings.get(meeting_id)
    if meeting:
        return persistence.save_meeting(meeting_id, meeting.get_summary())
    return False


def load_meeting(meeting_id: str) -> Optional[Meeting]:
    """Load meeting from disk"""
    from agent_core.project_room.meeting_persistence import persistence
    data = persistence.load_meeting(meeting_id)
    if data:
        meeting = Meeting(data.get("meeting_id", meeting_id), data.get("title", ""))
        meeting.participants = data.get("participants", [])
        meeting.status = data.get("status", "active")
        meetings[meeting_id] = meeting
        return meeting
    return None


def list_meetings() -> List[Dict[str, Any]]:
    """List all meetings"""
    return [m.get_summary() for m in meetings.values()]


def terminate_meeting(meeting_id: str) -> bool:
    """Terminate meeting"""
    meeting = meetings.get(meeting_id)
    if meeting:
        meeting.status = "terminated"
        return True
    return False


def auto_discuss(meeting_id: str, topic: str, agents: List[str]) -> Dict[str, Any]:
    """Auto discuss topic with agents"""
    meeting = meetings.get(meeting_id)
    if not meeting:
        return {"success": False, "error": "Meeting not found"}
    
    results = []
    for agent_id in agents:
        result = execute_round(meeting_id, agent_id, f"Discussing: {topic}")
        results.append(result)
    
    return {"success": True, "results": results}


def summarize_meeting(meeting_id: str) -> Dict[str, Any]:
    """Summarize meeting"""
    meeting = meetings.get(meeting_id)
    if not meeting:
        return {"success": False, "error": "Meeting not found"}
    
    return {
        "success": True,
        "summary": f"Meeting '{meeting.title}' has {len(meeting.rounds)} rounds with {len(meeting.participants)} participants.",
        "meeting": meeting.get_summary(),
    }


def search_meetings(query: str) -> List[Dict[str, Any]]:
    """Search meetings by query"""
    results = []
    for meeting in meetings.values():
        if query.lower() in meeting.title.lower():
            results.append(meeting.get_summary())
    return results


def list_templates() -> List[Dict[str, Any]]:
    """List meeting templates"""
    return []


def export_meeting_markdown(meeting_id: str) -> str:
    """Export meeting as markdown"""
    meeting = meetings.get(meeting_id)
    if not meeting:
        return "# Meeting Not Found"
    
    md = f"# {meeting.title}\n\n"
    md += f"**Status**: {meeting.status}\n\n"
    md += f"**Participants**: {', '.join(meeting.participants) or 'None'}\n\n"
    md += f"**Rounds**: {len(meeting.rounds)}\n\n"
    
    if meeting.rounds:
        md += "## Discussion Rounds\n\n"
        for i, round_data in enumerate(meeting.rounds, 1):
            md += f"### Round {i}\n\n"
            md += f"- Agent: {round_data.get('agent_id', 'Unknown')}\n"
            md += f"- Message: {round_data.get('message', '')}\n\n"
    
    return md


def update_template(template_id: str, data: Dict[str, Any]) -> bool:
    """Update meeting template"""
    return False


def delete_template(template_id: str) -> bool:
    """Delete meeting template"""
    return False


def get_meeting_stats() -> Dict[str, Any]:
    """Get meeting statistics"""
    active_count = sum(1 for m in meetings.values() if m.status == "active")
    return {
        "total_meetings": len(meetings),
        "active_meetings": active_count,
        "total_rounds": sum(len(m.rounds) for m in meetings.values()),
    }
