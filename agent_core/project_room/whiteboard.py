"""
Whiteboard - Project room whiteboard for collaboration
Each member can read/write to record requirements, decisions, tasks, issues, etc.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class WhiteboardItem:
    """Whiteboard item - can be task, note, decision, etc."""

    def __init__(self, item_id: str, item_type: str, content: str, author: str):
        self.id = item_id
        self.type = item_type
        self.content = content
        self.author = author
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


class Whiteboard:
    """Project room whiteboard"""

    def __init__(self, room_id: str):
        self.room_id = room_id
        self.items: Dict[str, WhiteboardItem] = {}

    def add_item(self, item_type: str, content: str, author: str) -> str:
        """Add item to whiteboard"""
        item_id = f"{len(self.items) + 1}"
        item = WhiteboardItem(item_id, item_type, content, author)
        self.items[item_id] = item
        return item_id

    def update_item(self, item_id: str, content: str) -> bool:
        """Update whiteboard item"""
        if item_id in self.items:
            self.items[item_id].content = content
            self.items[item_id].updated_at = datetime.now().isoformat()
            return True
        return False

    def delete_item(self, item_id: str) -> bool:
        """Delete whiteboard item"""
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False

    def get_items(self) -> List[Dict[str, Any]]:
        """Get all whiteboard items"""
        return [
            {
                "id": item.id,
                "type": item.type,
                "content": item.content,
                "author": item.author,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
            for item in self.items.values()
        ]


whiteboards: Dict[str, Whiteboard] = {}


def get_whiteboard(room_id: str) -> Whiteboard:
    """Get or create whiteboard for room"""
    if room_id not in whiteboards:
        whiteboards[room_id] = Whiteboard(room_id)
    return whiteboards[room_id]
