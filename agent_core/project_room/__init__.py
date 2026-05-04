"""
Project Room - Meeting and collaboration modules
"""

from agent_core.project_room.meeting import Meeting, get_meeting, create_meeting
from agent_core.project_room.whiteboard import Whiteboard, get_whiteboard
from agent_core.project_room.meeting_discussion import Discussion, get_discussion

__all__ = [
    'Meeting',
    'get_meeting',
    'create_meeting',
    'Whiteboard',
    'get_whiteboard',
    'Discussion',
    'get_discussion',
]
