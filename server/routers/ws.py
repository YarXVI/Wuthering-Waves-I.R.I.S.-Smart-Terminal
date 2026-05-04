"""
Router: WebSocket Real-time Whiteboard Events
Connect to ws://host/ws/{room_id} to receive whiteboard change notifications for that room.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from server.ws_manager import manager

router = APIRouter()


@router.websocket("/ws/{room_id}")
async def whiteboard_websocket(websocket: WebSocket, room_id: str):
    """
    Whiteboard real-time event push
    After client connects, it immediately enters the room. All whiteboard changes
    in that room (new entries, meeting status changes, etc.) will be pushed to the client in real-time.

    Message format:
        {"type": "entry_added", "entry": {...}}
        {"type": "meeting_status", "status": "developing", "consensus": true}
        {"type": "ping"}  # Server keepalive
    Client does not need to actively send messages, all communication is server push.
    """
    await manager.connect(websocket, room_id)
    try:
        while True:
            # Receive client messages (mainly for keepalive detection)
            try:
                data = await websocket.receive_text()
            except WebSocketDisconnect:
                break
            # Client can send "ping" for keepalive, server replies "pong"
            if data.strip() == "ping":
                try:
                    await websocket.send_text('{"type":"pong"}')
                except Exception:
                    break
    except Exception:
        pass
    finally:
        await manager.disconnect(websocket, room_id)
