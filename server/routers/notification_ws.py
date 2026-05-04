# I.R.I.S. Smart Terminal
# Copyright (C) 2024 I.R.I.S. Agent
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see
# <https://www.gnu.org/licenses/>.

"""
通知 WebSocket 端点
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import uuid

router = APIRouter()

_notifications_manager_map: dict[str, set[WebSocket]] = {}


@router.websocket("/ws/notifications/{client_id}")
async def notifications_websocket(websocket: WebSocket, client_id: str):
    await websocket.accept()
    if client_id not in _notifications_manager_map:
        _notifications_manager_map[client_id] = set()
    _notifications_manager_map[client_id].add(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_text()
            except WebSocketDisconnect:
                break
            if data.strip() == "ping":
                try:
                    await websocket.send_text('{"type":"pong"}')
                except Exception:
                    break
    except Exception:
        pass
    finally:
        if client_id in _notifications_manager_map:
            _notifications_manager_map[client_id].discard(websocket)


async def push_notification(client_id: str, notification: dict):
    """向指定客户端推送通知"""
    if client_id not in _notifications_manager_map:
        return
    payload = json.dumps({**notification, "type": "notification"})
    for ws in list(_notifications_manager_map.get(client_id, [])):
        try:
            await ws.send_text(payload)
        except Exception:
            _notifications_manager_map[client_id].discard(ws)


async def broadcast_notification(notification: dict):
    """向所有已连接客户端广播通知"""
    payload = json.dumps({**notification, "type": "notification"})
    for client_id, ws_list in list(_notifications_manager_map.items()):
        for ws in list(ws_list):
            try:
                await ws.send_text(payload)
            except Exception:
                ws_list.discard(ws)
