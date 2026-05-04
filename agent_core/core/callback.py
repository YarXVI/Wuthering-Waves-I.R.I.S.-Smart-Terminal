"""

回调机制 - Agent 执行过程中的事件钩子

支持可中断的 API 调用和状态监控

"""



from abc import ABC, abstractmethod

from dataclasses import dataclass, field

from enum import Enum

from typing import Any, Callable

import threading





class EventType(str, Enum):

    """事件类型枚举"""

    ON_START = "on_start"

    ON_END = "on_end"

    ON_ITERATION_START = "on_iteration_start"

    ON_ITERATION_END = "on_iteration_end"

    ON_TOOL_CALL_START = "on_tool_call_start"

    ON_TOOL_CALL_END = "on_tool_call_end"

    ON_TOOL_CALL_ERROR = "on_tool_call_error"

    ON_API_CALL_START = "on_api_call_start"

    ON_API_CALL_END = "on_api_call_end"

    ON_API_ERROR = "on_api_error"

    ON_COMPRESSION = "on_compression"

    ON_INTERRUPT_REQUESTED = "on_interrupt_requested"

    ON_MAX_ITERATIONS_REACHED = "on_max_iterations_reached"





@dataclass

class Event:

    """事件数据"""

    event_type: EventType

    data: dict = field(default_factory=dict)

    timestamp: float = 0.0





class CallbackHandler(ABC):

    """回调处理器抽象基类"""



    @abstractmethod

    def handle(self, event: Event) -> None:

        """处理事件"""

        pass





class CallbackManager:

    """回调管理器"""



    def __init__(self):

        self._handlers: dict[EventType, list[CallbackHandler]] = {}

        self._global_handlers: list[CallbackHandler] = []

        self._lock = threading.Lock()



    def register(self, event_type: EventType, handler: CallbackHandler) -> None:

        """注册单个事件处理器"""

        with self._lock:

            if event_type not in self._handlers:

                self._handlers[event_type] = []

            if handler not in self._handlers[event_type]:

                self._handlers[event_type].append(handler)



    def register_global(self, handler: CallbackHandler) -> None:

        """注册全局事件处理器（处理所有事件）"""

        with self._lock:

            if handler not in self._global_handlers:

                self._global_handlers.append(handler)



    def unregister(self, event_type: EventType, handler: CallbackHandler) -> None:

        """注销事件处理器"""

        with self._lock:

            if event_type in self._handlers:

                if handler in self._handlers[event_type]:

                    self._handlers[event_type].remove(handler)



    def trigger(self, event: Event) -> None:

        """触发事件"""

        with self._lock:

            handlers = list(self._handlers.get(event.event_type, []))

            global_handlers = list(self._global_handlers)



        for handler in handlers + global_handlers:

            try:

                handler.handle(event)

            except Exception as e:

                print(f"[CallbackHandler] Error handling {event.event_type}: {e}")





class InterruptibleContext:

    """可中断上下文"""



    def __init__(self):

        self._interrupted = False

        self._lock = threading.Lock()



    def interrupt(self) -> None:

        """请求中断"""

        with self._lock:

            self._interrupted = True



    def is_interrupted(self) -> bool:

        """检查是否被中断"""

        with self._lock:

            return self._interrupted



    def reset(self) -> None:

        """重置中断状态"""

        with self._lock:

            self._interrupted = False





class StateTracker:

    """状态跟踪器"""



    def __init__(self):

        self._state: dict[str, Any] = {}

        self._lock = threading.Lock()



    def set(self, key: str, value: Any) -> None:

        """设置状态"""

        with self._lock:

            self._state[key] = value



    def get(self, key: str, default: Any = None) -> Any:

        """获取状态"""

        with self._lock:

            return self._state.get(key, default)



    def update(self, updates: dict[str, Any]) -> None:

        """批量更新状态"""

        with self._lock:

            self._state.update(updates)



    def clear(self) -> None:

        """清除所有状态"""

        with self._lock:

            self._state.clear()



    def snapshot(self) -> dict[str, Any]:

        """获取状态快照"""

        with self._lock:

            return dict(self._state)





class LoggingCallback(CallbackHandler):

    """日志记录回调处理器"""



    def __init__(self, logger: Callable[[str], None] | None = None):

        self._logger = logger or print



    def handle(self, event: Event) -> None:

        """记录事件"""

        msg = f"[{event.event_type.value}]"

        if event.data:

            msg += f" {event.data}"

        self._logger(msg)





class MetricsCallback(CallbackHandler):

    """指标收集回调处理器"""



    def __init__(self):

        self._metrics: dict[str, int] = {}

        self._lock = threading.Lock()



    def handle(self, event: Event) -> None:

        """收集指标"""

        with self._lock:

            key = event.event_type.value

            self._metrics[key] = self._metrics.get(key, 0) + 1



    def get_metrics(self) -> dict[str, int]:

        """获取指标"""

        with self._lock:

            return dict(self._metrics)



    def reset(self) -> None:

        """重置指标"""

        with self._lock:

            self._metrics.clear()





class MaxIterationsCallback(CallbackHandler):

    """最大迭代次数回调"""



    def __init__(self, max_iterations: int = 10):

        self._max_iterations = max_iterations

        self._iteration_count = 0



    def handle(self, event: Event) -> None:

        """检查迭代次数"""

        if event.event_type == EventType.ON_ITERATION_END:

            self._iteration_count += 1

            if self._iteration_count >= self._max_iterations:

                print(f"[MaxIterationsCallback] Reached max iterations: {self._max_iterations}")



    def reset(self) -> None:

        """重置计数"""

        self._iteration_count = 0





def create_default_callback_manager() -> CallbackManager:

    """创建默认回调管理器"""

    manager = CallbackManager()

    manager.register_global(LoggingCallback())

    return manager

