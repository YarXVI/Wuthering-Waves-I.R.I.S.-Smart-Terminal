"""
记忆系统 — 持久化 Agent 对话历史 + 通用记忆管理
"""

from agent_core.memory.session_store import (
    save_session,
    load_session,
    delete_session,
    list_sessions,
)

from agent_core.memory.memory_store import (
    add_memory,
    get_memories,
    search_memories,
    delete_memory,
    clear_memories,
    stats as memory_stats,
)

__all__ = [
    # 会话存储
    "save_session", "load_session", "delete_session", "list_sessions",
    # 记忆存储
    "add_memory", "get_memories", "search_memories",
    "delete_memory", "clear_memories", "memory_stats",
]
