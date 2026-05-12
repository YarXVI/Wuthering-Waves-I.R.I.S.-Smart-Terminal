"""
IRIS LCM 集成测试
验证 agent_core.lcm 模块的正确性
"""
import pytest
from agent_core.lcm import (
    ContextChunk, LCMState, ChunkStore, LCMClient, LCMOrchestrator,
    TokenBudget, ChunkGraph, IRISLCMStore, IRISLCMClient, IRISLCMSessionManager,
)


class TestIRISLCMImport:
    """测试 IRIS LCM 模块导入"""

    def test_import_compatibility(self):
        """测试旧版接口兼容性"""
        assert ChunkStore is not None
        assert LCMClient is not None
        assert LCMOrchestrator is not None

    def test_import_v2_components(self):
        """测试 v2 组件导入"""
        from agent_core.lcm import ChunkStoreV2, LCMClientV2, LCMOrchestratorV2
        assert ChunkStoreV2 is not None
        assert LCMClientV2 is not None
        assert LCMOrchestratorV2 is not None


class TestIRISLCMStore:
    """测试 IRIS LCM Store 适配器"""

    def test_add_memory_entry(self):
        store = IRISLCMStore()
        chunk_id = store.add_memory_entry("entry_1", "test content", "test summary")
        assert chunk_id == "mem_entry_1"
        chunk = store.get_chunk_by_memory_id("entry_1")
        assert chunk is not None
        assert chunk.content == "test content"
        assert chunk.summary == "test summary"

    def test_build_index(self):
        store = IRISLCMStore()
        store.add_memory_entry("e1", "content about python", "python summary")
        store.add_memory_entry("e2", "content about java", "java summary")
        index = store.build_index_for_query("python")
        assert len(index) > 0


class TestIRISLCMClient:
    """测试 IRIS LCM Client"""

    def test_add_context(self):
        client = IRISLCMClient(llm_client=None)
        chunk_id = client.add_context_from_memory("m1", "memory content", "memory summary")
        assert chunk_id is not None
        chunk = client.store.get_chunk("mem_m1")
        assert chunk is not None
        assert chunk.content == "memory content"


class TestIRISLCMSessionManager:
    """测试 IRIS LCM 会话管理器"""

    def test_create_and_get_session(self):
        manager = IRISLCMSessionManager()
        client = manager.create_session("session_1", None)
        assert client is not None
        retrieved = manager.get_session("session_1")
        assert retrieved is client

    def test_end_session(self):
        manager = IRISLCMSessionManager()
        manager.create_session("session_1", None)
        manager.end_session("session_1")
        assert manager.get_session("session_1") is None

    def test_global_context(self):
        manager = IRISLCMSessionManager()
        manager.add_global_context("global content", "global summary", "global_1")
        store = manager.get_global_store()
        chunk = store.get_chunk("global_1")
        assert chunk is not None
        assert chunk.content == "global content"


class TestLCMV2Features:
    """测试 LCM v2 特性在 IRIS 集成中可用"""

    def test_token_budget(self):
        budget = TokenBudget(max_tokens=1000)
        assert budget.available_tokens > 0

    def test_chunk_graph(self):
        graph = ChunkGraph()
        graph.add_dependency("A", "B")
        deps = graph.get_dependencies("A")
        assert "B" in deps

    def test_store_operations(self):
        store = ChunkStore()
        store.add_chunk(ContextChunk(
            chunk_id="test",
            content="test content",
            summary="test",
        ))
        chunk = store.get_chunk("test")
        assert chunk is not None
        assert chunk.content == "test content"
