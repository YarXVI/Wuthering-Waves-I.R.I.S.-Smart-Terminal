"""
Router: Project Room Whiteboard
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from datetime import datetime
from agent_core.project_room.whiteboard import Whiteboard, WhiteboardItem, whiteboards, get_whiteboard
from server.ws_manager import manager as ws_manager
from server._async_utils import fire_and_forget

router = APIRouter()


class WhiteboardEntryRequest(BaseModel):
    """Add whiteboard entry"""
    author: str = "user"
    type: str = "note"
    content: str
    assigned_to: str = ""
    tags: list[str] = []


@router.get("/whiteboard/rooms")
def list_whiteboard_rooms():
    """List all meeting rooms (whiteboards)"""
    rooms = []
    for room_id, wb in whiteboards.items():
        items = wb.get_items()
        rooms.append({
            "room_id": room_id,
            "entry_count": len(items),
            "items": items,
        })
    return {"rooms": rooms, "total": len(rooms)}


@router.get("/whiteboard/rooms/{room_id}")
def get_whiteboard_room(room_id: str):
    """Get whiteboard room details"""
    wb = get_whiteboard(room_id)
    items = wb.get_items()
    return {
        "room_id": room_id,
        "entry_count": len(items),
        "items": items,
    }


@router.post("/whiteboard/rooms/{room_id}/items")
def add_whiteboard_item(room_id: str, req: WhiteboardEntryRequest):
    """Add item to whiteboard"""
    wb = get_whiteboard(room_id)
    item_id = wb.add_item(req.type, req.content, req.author)
    return {"success": True, "item_id": item_id}


@router.put("/whiteboard/rooms/{room_id}/items/{item_id}")
def update_whiteboard_item(room_id: str, item_id: str, req: WhiteboardEntryRequest):
    """Update whiteboard item"""
    wb = get_whiteboard(room_id)
    success = wb.update_item(item_id, req.content)
    return {"success": success}


@router.delete("/whiteboard/rooms/{room_id}/items/{item_id}")
def delete_whiteboard_item(room_id: str, item_id: str):
    """Delete whiteboard item"""
    wb = get_whiteboard(room_id)
    success = wb.delete_item(item_id)
    return {"success": success}
