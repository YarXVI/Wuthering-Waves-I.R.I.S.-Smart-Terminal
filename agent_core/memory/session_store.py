"""
会话存储 — 将 Agent 对话历史持久化到本地 JSON 文件
"""

import json
from datetime import datetime
from pathlib import Path
from agent_core.utils.text import strip_emoji, sanitize_messages
from agent_core.utils.filelock import locked_write


# 存储根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent / "memory" / "sessions"


def _ensure_dir():
    """确保存储目录存在"""
    BASE_DIR.mkdir(parents=True, exist_ok=True)


def _session_path(agent_id: str) -> Path:
    """获取指定 Agent 的会话文件路径"""
    return BASE_DIR / f"{agent_id}.json"


def save_session(agent_id: str, messages: list[dict]) -> None:
    """
    保存 Agent 的对话历史。
    自动清理 emoji、分离 system prompt（不重复存储）。
    """
    _ensure_dir()
    # 清理消息
    messages = sanitize_messages(messages)
    # 分离 system prompt
    system_msgs = [m for m in messages if m["role"] == "system"]
    chat_msgs = [m for m in messages if m["role"] != "system"]

    path = _session_path(agent_id)
    data = {
        "agent_id": agent_id,
        "system_prompt": system_msgs[0]["content"] if system_msgs else "",
        "messages": chat_msgs,
        "message_count": len(chat_msgs) // 2,  # user + assistant = 1 轮
        "updated_at": datetime.now().isoformat(),
    }

    # 如果文件存在，保留 created_at
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            data["created_at"] = existing.get("created_at", data.get("updated_at"))
        except (json.JSONDecodeError, Exception):
            data["created_at"] = data["updated_at"]
    else:
        data["created_at"] = data["updated_at"]

    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    if not locked_write(path, json_str):
        # 降级：普通写入
        with open(path, "w", encoding="utf-8") as f:
            f.write(json_str)


def load_session(agent_id: str) -> dict | None:
    """
    加载 Agent 的对话历史。
    自动验证并修复 tool_call 序列完整性。

    返回: {"system_prompt": str, "messages": list[dict]} 或 None
    """
    path = _session_path(agent_id)
    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        messages = data.get("messages", [])

        # 验证 tool_call 序列完整性
        cleaned = _validate_tool_sequence(messages)
        if len(cleaned) != len(messages):
            print(f"[Memory] Session '{agent_id}': fixed {len(messages) - len(cleaned)} orphaned tool call(s)")

        return {
            "system_prompt": data.get("system_prompt", ""),
            "messages": cleaned,
        }
    except (json.JSONDecodeError, Exception) as e:
        print(f"[Memory] Failed to load session for '{agent_id}': {e}")
        return None


def _validate_tool_sequence(messages: list[dict]) -> list[dict]:
    """
    验证并修复消息中的 tool_call 序列。
    - 移除末尾孤立的 assistant tool_call（没有后续 tool 响应）
    - 确保 tool 消息跟在对应的 tool_call 后
    """
    cleaned = []
    i = 0
    while i < len(messages):
        msg = messages[i]
        cleaned.append(msg)

        # 如果这条是 assistant 且有 tool_calls
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            tool_call_ids = {tc.get("id") for tc in msg["tool_calls"]}
            tool_count = 0

            j = i + 1
            while j < len(messages):
                next_msg = messages[j]
                if next_msg.get("role") == "tool":
                    tool_count += 1
                    cleaned.append(next_msg)
                    j += 1
                elif next_msg.get("role") == "assistant" and next_msg.get("tool_calls"):
                    break
                else:
                    break

            if tool_count < len(tool_call_ids):
                # tool 响应不完整，移除刚添加的 tool 消息和这个 assistant 消息
                while cleaned and cleaned[-1].get("role") == "tool":
                    cleaned.pop()
                cleaned.pop()
                i = j
                continue
            else:
                i = j
                continue

        i += 1

    return cleaned


def delete_session(agent_id: str) -> None:
    """删除指定 Agent 的会话文件"""
    path = _session_path(agent_id)
    if path.exists():
        path.unlink()


def archive_session(agent_id: str) -> str | None:
    """
    将当前会话存档（重命名为带时间戳的存档文件），
    然后删除原始会话文件，让下次启动时开启全新会话。

    返回存档文件名，如果无会话文件则返回 None。
    """
    _ensure_dir()
    path = _session_path(agent_id)
    if not path.exists():
        return None

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_path = BASE_DIR / f"{agent_id}.archive.{timestamp}.json"

    try:
        path.rename(archive_path)
        print(f"[Session] Archived '{agent_id}' -> {archive_path.name}")
        return archive_path.name
    except Exception as e:
        print(f"[Session] Failed to archive '{agent_id}': {e}")
        return None


def list_archived_sessions(agent_id: str) -> list[dict]:
    """列出指定 Agent 的所有存档会话摘要"""
    _ensure_dir()
    sessions = []
    for f in sorted(BASE_DIR.glob(f"{agent_id}.archive.*.json"), reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            sessions.append({
                "agent_id": data.get("agent_id", agent_id),
                "message_count": data.get("message_count", 0),
                "updated_at": data.get("updated_at", ""),
                "archived_file": f.name,
            })
        except Exception:
            pass
    return sessions


def list_sessions() -> list[dict]:
    """列出所有当前（未存档）会话摘要"""
    _ensure_dir()
    sessions = []
    for f in sorted(BASE_DIR.glob("*.json")):
        if ".archive." in f.name:
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            sessions.append({
                "agent_id": data.get("agent_id", f.stem),
                "message_count": data.get("message_count", 0),
                "updated_at": data.get("updated_at", ""),
            })
        except Exception:
            pass
    return sessions