"""
Meeting Persistence - 会议持久化存�?"""

import json
from pathlib import Path
from typing import Optional

from agent_core.project_room.meeting_models import MeetingSession, Round
from agent_core.utils.filelock import locked_write

MEMORY_DIR = Path(__file__).parent.parent.parent / "memory"
MEETINGS_DIR = MEMORY_DIR / "meetings"


def _ensure_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError):
        return False


def _meeting_path(room_id: str) -> Path:
    return MEETINGS_DIR / f"{room_id}.json"


def save_meeting(meeting: MeetingSession) -> bool:
    """持久化会议状态（带文件锁），失败静默降级"""
    if not _ensure_dir(MEETINGS_DIR):
        return False
    try:
        path = _meeting_path(meeting.room_id)
        json_str = json.dumps(meeting.to_dict(), ensure_ascii=False, indent=2)
        if not locked_write(path, json_str):
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_str)
        return True
    except (OSError, PermissionError, Exception):
        return False


def load_meeting(room_id: str) -> Optional[MeetingSession]:
    """从磁盘加载会议，不存在返�?None"""
    path = _meeting_path(room_id)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        meeting = MeetingSession(
            room_id=data["room_id"],
            topic=data.get("topic", ""),
            agents=data.get("agents", []),
            status=data.get("status", "discussing"),
            consensus=data.get("consensus", False),
            consensus_reason=data.get("consensus_reason", ""),
            artifacts=data.get("artifacts", {}),
            parent_room=data.get("parent_room", ""),
        )
        for r in data.get("rounds", []):
            meeting.rounds.append(Round(
                round_number=r["round_number"],
                author=r["author"],
                content=r["content"],
                type=r.get("type", "discussion"),
                timestamp=r.get("timestamp", 0),
            ))
        return meeting
    except (json.JSONDecodeError, OSError, PermissionError, Exception):
        return None


def list_meetings() -> list[dict]:
    """列出所有会�?""
    if not _ensure_dir(MEETINGS_DIR):
        return []
    meetings = []
    try:
        for f in sorted(MEETINGS_DIR.glob("*.json"), reverse=True):
            room_id = f.stem
            m = load_meeting(room_id)
            if m:
                meetings.append({
                    "room_id": m.room_id,
                    "topic": m.topic,
                    "status": m.status,
                    "agents": m.agents,
                    "round_count": len(m.rounds),
                    "consensus": m.consensus,
                    "last_round": m.rounds[-1].timestamp if m.rounds else 0,
                })
    except (OSError, PermissionError):
        pass
    return meetings


def delete_meeting(room_id: str) -> bool:
    """删除会议记录及关联的白板数据"""
    meeting_path = _meeting_path(room_id)
    if meeting_path.exists():
        try:
            meeting_path.unlink()
        except Exception:
            pass

    try:
        from agent_core.project_room.whiteboard import Whiteboard
        wb_path = Whiteboard._get_storage_dir_static() / f"{room_id}.json"
        if wb_path.exists():
            wb_path.unlink()
    except Exception:
        pass

    return not meeting_path.exists()