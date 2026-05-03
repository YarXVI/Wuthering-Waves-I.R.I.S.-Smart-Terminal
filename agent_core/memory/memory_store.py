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
记忆存储 — 通用记忆管理接口
支持不同类型的记忆条目，为后续增强（RAG、向量化等）预留扩展点。
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from agent_core.utils.filelock import locked_write


# 存储根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent / "memory" / "entries"


def _ensure_dir():
    BASE_DIR.mkdir(parents=True, exist_ok=True)


def _entries_path(agent_id: str) -> Path:
    return BASE_DIR / f"{agent_id}.json"


# ============================================================
# 核心操作
# ============================================================

def add_memory(agent_id: str, content: str, memory_type: str = "note", metadata: dict | None = None) -> dict:
    """
    添加一条记忆条目。

    参数:
        agent_id: 归属 Agent 的 ID（用 "global" 表示全局记忆）
        content: 记忆内容
        memory_type: 记忆类型（note, fact, preference, summary, custom...）
        metadata: 附加元数据（时间、来源、标签等）
    返回:
        创建的条目
    """
    _ensure_dir()
    path = _entries_path(agent_id)

    memories = []
    if path.exists():
        try:
            memories = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception):
            memories = []

    entry = {
        "id": f"{agent_id}_{datetime.now().timestamp():.6f}",
        "agent_id": agent_id,
        "type": memory_type,
        "content": content,
        "metadata": metadata or {},
        "created_at": datetime.now().isoformat(),
    }
    memories.append(entry)

    json_str = json.dumps(memories, ensure_ascii=False, indent=2)
    if not locked_write(path, json_str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(json_str)

    return entry


def get_memories(agent_id: str, memory_type: str | None = None, limit: int = 50) -> list[dict]:
    """
    获取指定 Agent 的记忆条目。

    参数:
        agent_id: Agent ID（"global" 获取全局记忆）
        memory_type: 可选，按类型过滤
        limit: 返回条数上限
    """
    path = _entries_path(agent_id)
    if not path.exists():
        return []

    try:
        memories = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception):
        return []

    if memory_type:
        memories = [m for m in memories if m.get("type") == memory_type]

    return memories[-limit:]


def search_memories(query: str, memory_type: str | None = None, limit: int = 20) -> list[dict]:
    """
    在所有记忆中进行关键词搜索。

    参数:
        query: 搜索关键词
        memory_type: 可选类型过滤
        limit: 返回条数上限
    返回:
        匹配的记忆条目列表
    """
    _ensure_dir()
    results = []

    for f in BASE_DIR.glob("*.json"):
        try:
            entries = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue

        for entry in entries:
            if memory_type and entry.get("type") != memory_type:
                continue
            if query.lower() in entry.get("content", "").lower():
                results.append(entry)

    return results[-limit:]


def delete_memory(agent_id: str, memory_id: str) -> bool:
    """删除指定记忆条目"""
    path = _entries_path(agent_id)
    if not path.exists():
        return False

    try:
        memories = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception):
        return False

    new_memories = [m for m in memories if m.get("id") != memory_id]
    if len(new_memories) == len(memories):
        return False

    json_str = json.dumps(new_memories, ensure_ascii=False, indent=2)
    if not locked_write(path, json_str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(json_str)
    return True


def clear_memories(agent_id: str) -> int:
    """清除指定 Agent 的所有记忆条目，返回删除数"""
    path = _entries_path(agent_id)
    if not path.exists():
        return 0

    try:
        memories = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception):
        return 0

    path.unlink()
    return len(memories)


def stats() -> dict:
    """记忆系统全局统计"""
    _ensure_dir()
    total_entries = 0
    agents = set()
    type_count: dict[str, int] = {}

    for f in BASE_DIR.glob("*.json"):
        try:
            entries = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        total_entries += len(entries)
        if entries:
            agents.add(f.stem)
        for e in entries:
            t = e.get("type", "unknown")
            type_count[t] = type_count.get(t, 0) + 1

    return {
        "total_entries": total_entries,
        "agents": sorted(agents),
        "types": type_count,
        "storage_path": str(BASE_DIR),
    }
