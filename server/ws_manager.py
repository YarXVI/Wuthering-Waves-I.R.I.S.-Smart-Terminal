"""
WebSocket Connection Manager - Manages real-time connections for multiple meeting rooms
"""

from typing import Dict, Set, Callable, Optional
from datetime import datetime
import asyncio


class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        self.rooms: Dict[str, Set[str]] = {}
        self.connections: Dict[str, asyncio.WebSocketServerProtocol] = {}
        self.last_activity: Dict[str, datetime] = {}
        self._cleanup_task: Optional[asyncio.Task] = None

    def add_connection(self, room_id: str, connection_id: str, ws):
        """Add a connection to a room"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(connection_id)
        self.connections[connection_id] = ws
        self.last_activity[connection_id] = datetime.now()

    def remove_connection(self, room_id: str, connection_id: str):
        """Remove a connection from a room"""
        if room_id in self.rooms:
            self.rooms[room_id].discard(connection_id)
        if connection_id in self.connections:
            del self.connections[connection_id]
        if connection_id in self.last_activity:
            del self.last_activity[connection_id]

    def broadcast(self, room_id: str, message: str):
        """Broadcast message to all connections in a room"""
        if room_id not in self.rooms:
            return
        for connection_id in self.rooms[room_id]:
            ws = self.connections.get(connection_id)
            if ws:
                asyncio.create_task(ws.send_text(message))

    def update_activity(self, connection_id: str):
        """Update last activity timestamp"""
        self.last_activity[connection_id] = datetime.now()

    def get_room_info(self, room_id: str) -> Dict:
        """Get room information"""
        return {
            "room_id": room_id,
            "connections": len(self.rooms.get(room_id, [])),
        }

    def start_cleanup(self):
        """Start background cleanup task for stale connections"""
        pass

    def stop_cleanup(self):
        """Stop background cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None


manager = ConnectionManager()


def start_cleanup():
    """Start background cleanup task for stale connections"""
    manager.start_cleanup()
