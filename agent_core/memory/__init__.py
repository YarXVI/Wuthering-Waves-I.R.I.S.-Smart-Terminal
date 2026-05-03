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
