"""
会话存储测试
"""
import sys
import os
import json
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent_core.memory.session_store import _validate_tool_sequence


class TestSessionStore:
    """会话存储工具函数测试"""

    def test_validate_tool_sequence_complete(self):
        """完整�?tool_call 序列应保持不�?""
        messages = [
            {"role": "user", "content": "search files"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"id": "call1", "type": "function", "function": {"name": "search", "arguments": "{}"}}],
            },
            {"role": "tool", "tool_call_id": "call1", "content": "result"},
            {"role": "assistant", "content": "here are the results"},
        ]
        cleaned = _validate_tool_sequence(messages)
        assert len(cleaned) == len(messages)

    def test_validate_tool_sequence_orphaned(self):
        """孤立�?tool_call（没�?tool 响应）应被移�?""
        messages = [
            {"role": "user", "content": "search files"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"id": "call1", "type": "function", "function": {"name": "search", "arguments": "{}"}}],
            },
            # 没有 tool 响应 �?应被移除
            {"role": "assistant", "content": "final answer"},
        ]
        cleaned = _validate_tool_sequence(messages)
        assert len(cleaned) == 2  # 只有 user 和最后一�?assistant


if __name__ == "__main__":
    pytest.main(["-v", __file__])
