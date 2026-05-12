"""
IRIS LCM Adapter
将 IRIS 核心组件与 LCM v2 集成的适配器层

提供：
1. Memory -> Chunk 自动转换
2. IRIS LLM 调用包装为 LCM 流
3. 会话状态与 IRIS 上下文同步
"""
from typing import Optional, List, Dict, Any, Callable, Iterator
from datetime import datetime

from prompt_experiment.lcm_v2 import (
    ContextChunk, LCMEvent, LCMSession, LCMState,
    ChunkStoreV2, LCMClientV2, LCMOrchestratorV2,
    TokenBudget, build_initial_messages_v2,
    get_logger,
)

logger = get_logger()


class IRISLCMStore:
    """
    IRIS 内存到 LCM ChunkStore 的适配器
    
    自动将 IRIS 的 memory entries 转换为 LCM chunks
    """

    def __init__(self, chunk_store: Optional[ChunkStoreV2] = None):
        self.store = chunk_store or ChunkStoreV2()
        self._memory_map: Dict[str, str] = {}  # memory_id -> chunk_id

    def add_memory_entry(self, entry_id: str, content: str, summary: str = "",
                         source: str = "memory", metadata: Optional[Dict] = None) -> str:
        """
        将 IRIS memory entry 添加为 LCM chunk
        
        Returns:
            chunk_id
        """
        chunk_id = f"mem_{entry_id}"
        self.store.add_chunk(ContextChunk(
            chunk_id=chunk_id,
            content=content,
            summary=summary or content[:100],
            source=source,
            metadata=metadata or {"iris_entry_id": entry_id},
        ))
        self._memory_map[entry_id] = chunk_id
        logger.info("Memory entry converted to LCM chunk", entry_id=entry_id, chunk_id=chunk_id)
        return chunk_id

    def get_chunk_by_memory_id(self, entry_id: str) -> Optional[ContextChunk]:
        """通过 IRIS memory ID 获取 chunk"""
        chunk_id = self._memory_map.get(entry_id)
        if chunk_id:
            return self.store.get_chunk(chunk_id)
        return None

    def build_index_for_query(self, query: str) -> List[Dict[str, str]]:
        """
        为 IRIS 查询构建 chunk 索引
        
        Returns:
            摘要列表，用于构建 LCM prompt
        """
        summaries = self.store.list_summaries()
        # 简单过滤：只返回与查询相关的 chunks
        query_lower = query.lower()
        filtered = [
            s for s in summaries
            if query_lower in s.get("summary", "").lower()
            or query_lower in s.get("chunk_id", "").lower()
        ]
        return filtered if filtered else summaries[:20]  # 最多返回20个


class IRISLCMClient:
    """
    IRIS LCM 客户端
    
    包装 IRIS 的 LLM 调用，提供 LCM 增强的对话能力
    """

    def __init__(self, llm_client: Any, chunk_store: Optional[ChunkStoreV2] = None):
        self.llm_client = llm_client
        self.store = chunk_store or ChunkStoreV2()
        self.lcm_client = LCMClientV2(llm_client=llm_client, chunk_store=self.store)

    def chat_with_context(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 8000,
        **kwargs
    ) -> str:
        """
        使用 LCM 进行上下文增强的对话
        
        Args:
            messages: 消息列表
            system_prompt: 系统提示（可选）
            max_tokens: 最大 token 数
            **kwargs: 额外的 LLM 参数
        
        Returns:
            生成的回复
        """
        # 构建 LCM 初始消息
        if system_prompt:
            initial_messages = [{"role": "system", "content": system_prompt}] + messages
        else:
            initial_messages = messages

        # 使用 IRIS LLM 包装器
        def stream_fn(msgs):
            return self._iris_stream_wrapper(msgs, **kwargs)

        try:
            result = self.lcm_client.chat(initial_messages, stream_fn)
            return result
        except Exception as e:
            logger.error("LCM chat failed", error=str(e))
            # 降级：直接调用 LLM
            return self._direct_llm_call(initial_messages, **kwargs)

    def _iris_stream_wrapper(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """将 IRIS LLM 调用包装为流式生成器"""
        try:
            # 假设 IRIS LLM 有 generate/stream 方法
            if hasattr(self.llm_client, "stream"):
                response = self.llm_client.stream(messages, **kwargs)
                for chunk in response:
                    if hasattr(chunk, "content"):
                        yield chunk.content
                    elif isinstance(chunk, str):
                        yield chunk
                    elif isinstance(chunk, dict) and "content" in chunk:
                        yield chunk["content"]
            elif hasattr(self.llm_client, "generate"):
                # 非流式，模拟流式
                response = self.llm_client.generate(messages, **kwargs)
                content = response.content if hasattr(response, "content") else str(response)
                # 模拟流式输出
                for i in range(0, len(content), 10):
                    yield content[i:i+10]
            else:
                raise ValueError("LLM client must have 'stream' or 'generate' method")
        except Exception as e:
            logger.error("IRIS stream wrapper failed", error=str(e))
            raise

    def _direct_llm_call(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """直接调用 LLM（降级方案）"""
        if hasattr(self.llm_client, "generate"):
            response = self.llm_client.generate(messages, **kwargs)
            return response.content if hasattr(response, "content") else str(response)
        return ""

    def add_context_from_memory(self, entry_id: str, content: str, summary: str = "") -> str:
        """从 IRIS memory 添加上下文"""
        chunk_id = f"mem_{entry_id}"
        self.lcm_client.store.add_chunk(ContextChunk(
            chunk_id=chunk_id,
            content=content,
            summary=summary or content[:100],
            source="iris_memory",
        ))
        return chunk_id

    def get_stats(self) -> Dict[str, Any]:
        """获取 LCM 统计信息"""
        return self.lcm_client.stats_report()


class IRISLCMSessionManager:
    """
    IRIS LCM 会话管理器
    
    管理多个 LCM 会话，与 IRIS 的 session 系统同步
    """

    def __init__(self):
        self._sessions: Dict[str, IRISLCMClient] = {}
        self._store = ChunkStoreV2()

    def create_session(self, session_id: str, llm_client: Any) -> IRISLCMClient:
        """创建新的 LCM 会话"""
        client = IRISLCMClient(llm_client=llm_client, chunk_store=self._store)
        self._sessions[session_id] = client
        logger.info("LCM session created", session_id=session_id)
        return client

    def get_session(self, session_id: str) -> Optional[IRISLCMClient]:
        """获取已有会话"""
        return self._sessions.get(session_id)

    def end_session(self, session_id: str) -> None:
        """结束会话"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info("LCM session ended", session_id=session_id)

    def add_global_context(self, content: str, summary: str, chunk_id: str) -> None:
        """添加全局上下文（所有会话共享）"""
        self._store.add_chunk(ContextChunk(
            chunk_id=chunk_id,
            content=content,
            summary=summary,
            source="global",
        ))

    def get_global_store(self) -> ChunkStoreV2:
        """获取全局存储"""
        return self._store
