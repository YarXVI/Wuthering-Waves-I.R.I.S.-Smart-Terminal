"""
LCM Engine

Core protocol implementation for Lazy Context Materialization.
Integrates chunk storage, sentinel detection, and state machine.
"""
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Generator, Callable
from enum import Enum

from agent_core.v2.infrastructure.chunk_store import ChunkStore, Chunk
from agent_core.v2.infrastructure.sentinel_detector import SentinelDetector, LoadRequest
from agent_core.v2.infrastructure.content_encoding import (
    ContentEncodingRegistry, EncodingType, EncodingContext
)


class LCMState(Enum):
    """LCM 状态机"""
    IDLE = "idle"
    GENERATING = "generating"
    WAITING_CHUNK = "waiting_chunk"
    RESUMING = "resuming"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class LCMEvent:
    """LCM 事件"""
    event_type: str
    chunk_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LCMSession:
    """LCM 会话"""
    session_id: str
    state: LCMState = LCMState.IDLE
    total_chunks_loaded: int = 0
    load_history: List[LCMEvent] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    @property
    def duration_ms(self) -> float:
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds() * 1000


@dataclass
class LCMConfig:
    """LCM 配置"""
    max_rounds: int = 20
    max_prefetch: int = 3
    enable_prefetch: bool = True
    retry_attempts: int = 2
    # 内容编码配置
    encoding_type: EncodingType = EncodingType.IDENTITY
    encoding_registry: Optional[ContentEncodingRegistry] = None


class LCMEngine:
    """
    V2 原生 LCM 引擎

    职责：
    1. 管理 Chunk 存储（通过 ChunkStore）
    2. 检测哨兵标记（通过 SentinelDetector）
    3. 执行状态机（IDLE -> GENERATING -> WAITING_CHUNK -> RESUMING -> COMPLETED）
    4. 处理 chunk 加载和注入
    5. 收集指标
    """

    def __init__(
        self,
        chunk_store: Optional[ChunkStore] = None,
        config: Optional[LCMConfig] = None,
    ):
        self.store = chunk_store or ChunkStore()
        self.config = config or LCMConfig()
        self.detector = SentinelDetector()
        self.session: Optional[LCMSession] = None
        self._round = 0
        self._event_handlers: List[Callable[[LCMEvent], None]] = []
        # 初始化内容编码
        self._encoding_registry = self.config.encoding_registry or ContentEncodingRegistry()
        self._encoding_context = EncodingContext()

    def _get_encoder(self):
        """获取当前配置的编码器"""
        return self._encoding_registry.get(self.config.encoding_type)

    def register_encoding(self, encoding):
        """注册内容编码"""
        self._encoding_registry.register(encoding)
        return self

    def set_encoding(self, encoding_type: EncodingType):
        """设置内容编码类型"""
        self.config.encoding_type = encoding_type
        return self

    def on_event(self, handler: Callable[[LCMEvent], None]) -> None:
        """注册事件处理器"""
        self._event_handlers.append(handler)

    def _emit(self, event_type: str, chunk_id: str = "", **metadata) -> None:
        """发送事件"""
        event = LCMEvent(
            event_type=event_type,
            chunk_id=chunk_id,
            metadata=metadata,
        )
        if self.session:
            self.session.load_history.append(event)
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception:
                pass

    def new_session(self, session_id: str = "") -> LCMSession:
        """创建新会话"""
        sid = session_id or f"lcm_{int(time.time() * 1000)}"
        self.session = LCMSession(session_id=sid, state=LCMState.IDLE)
        self.detector.reset()
        self._round = 0
        return self.session

    def build_index_section(self) -> str:
        """构建 chunk 索引文本"""
        summaries = self.store.list_summaries()
        if not summaries:
            return "[无可用上下文块]"

        lines = ["## 可用上下文块索引", ""]
        for s in summaries:
            lines.append(
                f"- **{s['chunk_id']}** [{s.get('source', 'unknown')}] "
                f"({s['tokens']} tokens, 加载 {s.get('load_count', 0)} 次): {s['summary']}"
            )
        return "\n".join(lines)

    def build_system_prompt(self, base_prompt: str, user_query: str = "") -> str:
        """构建包含 LCM 协议指令的系统提示词

        如果配置了内容编码，会在系统提示词中注入编码指令。
        """
        # 更新编码上下文
        self._encoding_context.user_query = user_query
        self._encoding_context.session_id = self.session.session_id if self.session else ""

        # 应用内容编码
        encoder = self._get_encoder()
        encoded_base = encoder.encode_system_prompt(base_prompt, self._encoding_context)

        lcm_instructions = """你是一个具备「惰性上下文物化」（Lazy Context Materialization）能力的 AI 助手。

## 核心机制

你的上下文窗口包含**上下文块的摘要索引**，而非完整内容。当你需要某个块的详细内容才能继续回答时，使用哨兵标记请求加载：

```
[NEED_CHUNK:chunk_id]
```

系统会立即将对应块的完整内容注入你的上下文，然后请你继续。

## 使用规则

1. **引用代码细节必须先请求**：如果你要在回答中引用具体的代码行、变量名、字符串字面量、函数参数等细节，必须先用 [NEED_CHUNK:id] 请求该块。
2. **可以基于摘要做宏观判断**：如果只需讨论架构模式、风险类型等高层面内容而不涉及具体代码行，可以直接回答。
3. **每次只请求一个块**：一个 [NEED_CHUNK:id] 标记对应一个块。如需多个块，依次请求。
4. **请求后立即停止**：发出 [NEED_CHUNK:id] 后不要继续生成，等待系统注入。
5. **不要编造代码**：如果你不记得某段代码的具体内容，请求对应的 chunk，绝对不要凭摘要臆造变量名或值。
6. **chunk_id 必须精确**：使用摘要列表中给出的确切 chunk_id。
7. **续接时直接继续**：系统注入 chunk 后，请从被打断的位置直接继续分析。**不要重复之前的开场白。**

## 重要提醒

- 不要输出 [NEED_CHUNK:xxx] 以外的格式
- 如果在摘要中已经能看到足够信息，直接回答，不要请求
- 请求加载的 chunk 内容会完整出现在你的上下文中
"""
        index_section = self.build_index_section()
        result = f"{encoded_base}\n\n{lcm_instructions}\n\n{index_section}"

        # 对完整系统提示词再次应用编码（确保 LCM 指令也被编码）
        return encoder.encode_system_prompt(result, self._encoding_context)

    def process_response(self, response_text: str) -> tuple[str, List[LoadRequest]]:
        """
        处理模型响应，检测哨兵标记

        如果配置了内容编码，会在检测前对响应进行编码处理
        （如提取思考链、压缩文本等）。

        Returns:
            (clean_text, load_requests)
        """
        # 应用内容编码到响应
        encoder = self._get_encoder()
        self._encoding_context.current_round = self._round
        encoded_response = encoder.encode_response(response_text, self._encoding_context)

        self.detector.reset()
        requests = self.detector.feed(encoded_response)
        clean_text = self.detector.get_clean_buffer()

        if requests:
            self._emit("sentinel_detected", requests[0].chunk_id, count=len(requests))

        return clean_text, requests

    def load_chunk(self, chunk_id: str) -> Optional[Chunk]:
        """加载 chunk"""
        chunk = self.store.get(chunk_id)
        if chunk:
            self._emit("chunk_loaded", chunk_id, tokens=chunk.tokens)
            if self.session:
                self.session.total_chunks_loaded += 1
                self.session.state = LCMState.RESUMING
        else:
            self._emit("chunk_not_found", chunk_id)
        return chunk

    def inject_chunk(self, messages: List[Dict[str, str]], chunk: Chunk) -> List[Dict[str, str]]:
        """将 chunk 注入到消息列表中"""
        messages.append({
            "role": "system",
            "content": f"[已加载上下文块: {chunk.chunk_id}]\n{chunk.content}",
        })
        self._emit("chunk_injected", chunk.chunk_id)
        return messages

    def run_sync(
        self,
        messages: List[Dict[str, str]],
        stream_fn: Callable[[List[Dict[str, str]]], str],
        session_id: str = "",
    ) -> str:
        """同步执行 LCM 会话"""
        self.new_session(session_id)
        current_messages = list(messages)
        self.session.state = LCMState.GENERATING
        self._emit("generation_started")

        while self._round < self.config.max_rounds:
            self._round += 1

            response = stream_fn(current_messages)
            clean_text, requests = self.process_response(response)

            if not requests:
                self.session.state = LCMState.COMPLETED
                self.session.end_time = datetime.now()
                self._emit("completed", rounds=self._round)
                return clean_text

            # 加载请求的 chunk
            req = requests[0]
            chunk = self.load_chunk(req.chunk_id)
            if chunk:
                current_messages = self.inject_chunk(current_messages, chunk)
            else:
                self.session.state = LCMState.ERROR
                self.session.end_time = datetime.now()
                self._emit("error", reason="chunk_not_found")
                return clean_text + f"\n[错误: 未找到 chunk '{req.chunk_id}']"

        self.session.state = LCMState.ERROR
        self.session.end_time = datetime.now()
        self._emit("error", reason="max_rounds_exceeded")
        return clean_text + "\n[错误: 达到最大轮次限制]"

    def run_stream(
        self,
        messages: List[Dict[str, str]],
        stream_fn: Callable[[List[Dict[str, str]]], Generator[str, None, None]],
        session_id: str = "",
    ) -> Generator[str, None, None]:
        """流式执行 LCM 会话"""
        self.new_session(session_id)
        current_messages = list(messages)
        self.session.state = LCMState.GENERATING
        self._emit("generation_started")

        while self._round < self.config.max_rounds:
            self._round += 1
            full_response = ""

            for chunk_text in stream_fn(current_messages):
                full_response += chunk_text
                requests = self.detector.feed(chunk_text)

                if requests:
                    break
                yield chunk_text

            clean_text = self.detector.get_clean_buffer()
            requests = self.detector.get_requests()

            if not requests:
                self.session.state = LCMState.COMPLETED
                self.session.end_time = datetime.now()
                self._emit("completed", rounds=self._round)
                yield clean_text
                return

            req = requests[0]
            chunk = self.load_chunk(req.chunk_id)
            if chunk:
                current_messages = self.inject_chunk(current_messages, chunk)
            else:
                self.session.state = LCMState.ERROR
                self.session.end_time = datetime.now()
                self._emit("error", reason="chunk_not_found")
                yield clean_text + f"\n[错误: 未找到 chunk '{req.chunk_id}']"
                return

        self.session.state = LCMState.ERROR
        self.session.end_time = datetime.now()
        self._emit("error", reason="max_rounds_exceeded")
        yield clean_text + "\n[错误: 达到最大轮次限制]"

    def get_stats(self) -> Dict[str, Any]:
        """获取 LCM 统计信息"""
        store_stats = self.store.get_stats()
        encoder = self._get_encoder()
        encoding_stats = encoder.get_stats()
        return {
            **store_stats,
            "session_id": self.session.session_id if self.session else None,
            "state": self.session.state.value if self.session else None,
            "rounds": self._round,
            "chunks_loaded": self.session.total_chunks_loaded if self.session else 0,
            "duration_ms": self.session.duration_ms if self.session else 0,
            "encoding": {
                "type": self.config.encoding_type.value,
                "name": encoder.name,
                **encoding_stats,
            },
            "available_encodings": self._encoding_registry.list_encodings(),
        }
