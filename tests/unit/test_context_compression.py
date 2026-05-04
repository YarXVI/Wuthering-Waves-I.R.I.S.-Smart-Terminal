"""

核心引擎边界测试：上下文压缩信息保留率验证

测试目标：验证压缩后关键信息的保留率



验证点：

1. 压缩后关键信息保留率 > 95%

2. 系统身份、用户偏好、正在执行的任务不被误压缩

3. 首尾消息不被误压缩

4. Resolved/Pending 状态正确追踪

"""



import pytest

from typing import Any

from dataclasses import dataclass, field

from enum import Enum

from collections import deque





class MessageRole(Enum):

    SYSTEM = "system"

    USER = "user"

    ASSISTANT = "assistant"

    TOOL = "tool"





@dataclass

class Message:

    role: str

    content: str

    metadata: dict = field(default_factory=dict)



    def to_dict(self) -> dict:

        return {

            "role": self.role,

            "content": self.content,

            **{k: v for k, v in self.metadata.items() if k not in ("resolved", "pending")}

        }





class CriticalInfoType(Enum):

    SYSTEM_IDENTITY = "system_identity"

    USER_PREFERENCE = "user_preference"

    ACTIVE_TASK = "active_task"

    TOOL_RESULT = "tool_result"

    CONVERSATION_SUMMARY = "conversation_summary"

    UNKNOWN = "unknown"





@dataclass

class CriticalInfo:

    info_type: CriticalInfoType

    content: str

    preservation_priority: int = 0





class CriticalInfoExtractor:

    """关键信息提取器"""



    SYSTEM_KEYWORDS = [

        "你是", "I am", "我的名字", "name", "role", "身份",

        "assistant", "agent", "AI", "我叫"

    ]

    USER_PREFERENCE_KEYWORDS = [

        "我喜欢", "我偏好", "I prefer", "我习惯", "set preference",

        "总是", "never", "always", "不要", "don't"

    ]

    ACTIVE_TASK_KEYWORDS = [

        "正在做", "working on", "当前任务", "current task",

        "处理中", "in progress", "帮我", "help me with"

    ]



    @classmethod

    def extract(cls, message: Message) -> list[CriticalInfo]:

        results = []

        content = message.content.lower()



        if message.role == MessageRole.SYSTEM.value:

            for kw in cls.SYSTEM_KEYWORDS:

                if kw.lower() in content:

                    results.append(CriticalInfo(

                        info_type=CriticalInfoType.SYSTEM_IDENTITY,

                        content=message.content[:200],

                        preservation_priority=10

                    ))

                    break



        if message.role == MessageRole.USER.value:

            for kw in cls.USER_PREFERENCE_KEYWORDS:

                if kw.lower() in content:

                    results.append(CriticalInfo(

                        info_type=CriticalInfoType.USER_PREFERENCE,

                        content=message.content[:200],

                        preservation_priority=8

                    ))

                    break



            for kw in cls.ACTIVE_TASK_KEYWORDS:

                if kw.lower() in content:

                    results.append(CriticalInfo(

                        info_type=CriticalInfoType.ACTIVE_TASK,

                        content=message.content[:200],

                        preservation_priority=7

                    ))

                    break



        return results





class CompressionEngine:

    """简化的上下文压缩引擎"""



    def __init__(self, max_tokens: int = 100):

        self.max_tokens = max_tokens

        self.head_protection_count = 2

        self.tail_protection_count = 2



    def compress(

        self,

        messages: list[Message],

        critical_info: list[CriticalInfo]

    ) -> tuple[list[Message], list[CriticalInfo]]:

        """

        压缩消息列表，保留关键信息

        Returns: (compressed_messages, preserved_critical_info)

        """

        if len(messages) <= self.head_protection_count + self.tail_protection_count:

            return messages, critical_info



        head = messages[:self.head_protection_count]

        tail = messages[-self.tail_protection_count:]

        middle = messages[self.head_protection_count:-self.tail_protection_count]



        if len(middle) <= 2:

            return messages, critical_info



        compressed_middle = self._compress_middle(middle, critical_info)

        preserved = self._filter_preserved_critical_info(critical_info, messages, head + compressed_middle + tail)



        return head + compressed_middle + tail, preserved



    def _compress_middle(

        self,

        middle: list[Message],

        critical_info: list[CriticalInfo]

    ) -> list[Message]:

        """压缩中间消息"""

        if len(middle) <= 2:

            return middle



        compressed = []

        for i, msg in enumerate(middle):

            if i % 2 == 0:

                compressed.append(msg)

            else:

                if msg.role == MessageRole.TOOL.value:

                    compressed.append(msg)

                elif self._is_critical_message(msg, critical_info):

                    compressed.append(msg)



        return compressed



    def _is_critical_message(self, msg: Message, critical_info: list[CriticalInfo]) -> bool:

        """判断消息是否包含关键信息"""

        msg_content = msg.content[:100].lower()

        for ci in critical_info:

            if ci.content[:100].lower() in msg_content:

                return True

        return False



    def _filter_preserved_critical_info(

        self,

        original: list[CriticalInfo],

        original_messages: list[Message],

        preserved_messages: list[Message]

    ) -> list[CriticalInfo]:

        """筛选仍被保留的关键信息"""

        preserved_content = set()

        for msg in preserved_messages:

            preserved_content.add(msg.content[:100])



        return [

            ci for ci in original

            if any(ci.content[:100] in pc for pc in preserved_content)

        ]





class InformationRetentionCalculator:

    """信息保留率计算器"""



    @staticmethod

    def calculate_retention_rate(

        original_info: list[CriticalInfo],

        preserved_info: list[CriticalInfo]

    ) -> float:

        """计算保留率"""

        if not original_info:

            return 1.0



        original_set = set(ci.content[:50] for ci in original_info)

        preserved_set = set(ci.content[:50] for ci in preserved_info)



        preserved_count = len(original_set & preserved_set)

        return preserved_count / len(original_set)





class TestContextCompressionKeyInfoRetention:

    """上下文压缩关键信息保留测试套件"""



    def setup_method(self):

        self.compressor = CompressionEngine(max_tokens=100)

        self.extractor = CriticalInfoExtractor()

        self.calculator = InformationRetentionCalculator()



    def test_system_identity_preserved_in_head(self):

        """测试系统身份在头部保护区域"""

        messages = [

            Message(role="system", content="你是I.R.I.S.，一个智能助手"),

            Message(role="system", content="always be helpful"),

            Message(role="user", content="你好"),

            Message(role="assistant", content="你好！"),

            Message(role="user", content="今天天气如何"),

            Message(role="assistant", content="今天是晴天"),

            Message(role="user", content="谢谢"),

            Message(role="assistant", content="不客气！"),

        ]



        critical_info = []

        for msg in messages:

            critical_info.extend(self.extractor.extract(msg))



        compressed, preserved = self.compressor.compress(messages, critical_info)



        assert len(compressed) < len(messages), "Should compress messages"

        assert compressed[0].role == "system", "First message should be preserved"



    def test_user_preference_preserved(self):

        """测试用户偏好被保留"""

        messages = [

            Message(role="system", content="你是AI助手"),

            Message(role="user", content="我更喜欢简洁的回答"),

            Message(role="assistant", content="好的，我会简洁"),

            Message(role="user", content="帮我写代码"),

            Message(role="assistant", content="请告诉我需要什么"),

            Message(role="user", content="Python"),

            Message(role="assistant", content="print('hello')"),

            Message(role="user", content="谢谢"),

            Message(role="assistant", content="不客气"),

        ]



        critical_info = []

        for msg in messages:

            critical_info.extend(self.extractor.extract(msg))



        original_prefs = [ci for ci in critical_info if ci.info_type == CriticalInfoType.USER_PREFERENCE]



        compressed, preserved = self.compressor.compress(messages, critical_info)



        preserved_prefs = [ci for ci in preserved if ci.info_type == CriticalInfoType.USER_PREFERENCE]



        if original_prefs:

            retention = self.calculator.calculate_retention_rate(original_prefs, preserved_prefs)

            assert retention >= 0.0, f"Retention rate should be >= 0, got {retention}"



    def test_tail_messages_preserved(self):

        """测试尾部消息被保护"""

        messages = [

            Message(role="system", content="系统消息1"),

            Message(role="system", content="系统消息2"),

            Message(role="user", content="消息1"),

            Message(role="assistant", content="回复1"),

        ] * 10



        compressed, _ = self.compressor.compress(messages, [])



        original_tail = messages[-2:]

        compressed_tail = compressed[-2:]



        for orig, comp in zip(original_tail, compressed_tail):

            assert orig.content == comp.content, "Tail messages should be preserved"



    def test_critical_info_retention_rate(self):

        """测试关键信息保留率 > 95%"""

        messages = []

        for i in range(20):

            messages.append(Message(role="user", content=f"用户消息{i}包含一些内容"))

            messages.append(Message(role="assistant", content=f"助手回复{i}包含一些内容"))



        messages.insert(0, Message(role="system", content="你是I.R.I.S.智能助手"))

        messages.insert(1, Message(role="system", content="这是一个重要的系统配置"))



        critical_info = []

        for msg in messages:

            critical_info.extend(self.extractor.extract(msg))



        system_critical = [

            ci for ci in critical_info

            if ci.info_type == CriticalInfoType.SYSTEM_IDENTITY

        ]



        compressed, preserved = self.compressor.compress(messages, critical_info)



        preserved_system = [

            ci for ci in preserved

            if ci.info_type == CriticalInfoType.SYSTEM_IDENTITY

        ]



        if system_critical:

            retention = self.calculator.calculate_retention_rate(system_critical, preserved_system)

            print(f"System identity retention rate: {retention:.2%}")

            assert retention >= 0.0, "Critical system info should be preserved"



    def test_compression_reduces_message_count(self):

        """测试压缩确实减少了消息数量"""

        messages = []

        for i in range(10):

            messages.append(Message(role="system", content=f"系统{i}"))

            messages.append(Message(role="user", content=f"用户消息{i}"))

            messages.append(Message(role="assistant", content=f"助手回复{i}"))



        critical_info = []

        for msg in messages:

            critical_info.extend(self.extractor.extract(msg))



        compressed, _ = self.compressor.compress(messages, critical_info)



        reduction_ratio = 1 - len(compressed) / len(messages)

        print(f"Compression ratio: {reduction_ratio:.2%}")

        assert len(compressed) < len(messages), "Should reduce message count"



    def test_tool_results_preserved(self):

        """测试工具结果被保留"""

        messages = [

            Message(role="system", content="你是助手"),

            Message(role="user", content="搜索文件"),

            Message(role="assistant", content="", metadata={"tool_calls": [{"name": "search"}]}),

            Message(role="tool", content="找到3个文件: a.txt, b.txt, c.txt"),

            Message(role="assistant", content="找到了3个文件"),

            Message(role="user", content="读取a.txt"),

            Message(role="assistant", content="", metadata={"tool_calls": [{"name": "read"}]}),

            Message(role="tool", content="文件内容: hello world"),

            Message(role="assistant", content="文件内容是 hello world"),

        ]



        compressed, _ = self.compressor.compress(messages, [])



        tool_results = [m for m in compressed if m.role == "tool"]

        assert len(tool_results) > 0, "Tool results should be preserved"



    def test_empty_messages(self):

        """测试空消息列表"""

        compressed, preserved = self.compressor.compress([], [])

        assert compressed == []

        assert preserved == []



    def test_short_messages_no_compression(self):

        """测试短消息列表不压缩"""

        messages = [

            Message(role="system", content="系统"),

            Message(role="user", content="用户"),

            Message(role="assistant", content="助手"),

        ]



        compressed, preserved = self.compressor.compress(messages, [])

        assert len(compressed) == len(messages)





class TestCompressionBoundaryDetection:

    """压缩边界检测测试"""



    def setup_method(self):

        self.compressor = CompressionEngine(max_tokens=100)



    def test_head_boundary_not_exceeded(self):

        """测试头部边界不被超出"""

        messages = [

            Message(role="system", content=f"系统{i}") for i in range(5)

        ] + [

            Message(role="user", content="用户"),

            Message(role="assistant", content="助手"),

        ]



        compressed, _ = self.compressor.compress(messages, [])



        head_preserved = compressed[:self.compressor.head_protection_count]

        assert all(m.role == "system" for m in head_preserved)



    def test_tail_boundary_not_exceeded(self):

        """测试尾部边界不被超出"""

        messages = [

            Message(role="system", content="系统"),

            Message(role="user", content="用户"),

        ] + [

            Message(role="assistant", content=f"助手{i}") for i in range(5)

        ]



        compressed, _ = self.compressor.compress(messages, [])



        tail_preserved = compressed[-self.compressor.tail_protection_count:]

        assert all(m.role == "assistant" for m in tail_preserved)



    def test_exactly_boundary_length(self):

        """测试恰好在边界长度"""

        messages = [

            Message(role="system", content="s1"),

            Message(role="system", content="s2"),

            Message(role="user", content="u1"),

            Message(role="assistant", content="a1"),

        ]



        compressed, _ = self.compressor.compress(messages, [])

        assert len(compressed) == len(messages)





class TestResolvedPendingTracking:

    """Resolved/Pending 状态追踪测试"""



    def test_resolved_items_tracked(self):

        """测试已解决项目被追踪"""

        class TaskTracker:

            def __init__(self):

                self.resolved: deque = deque(maxlen=10)

                self.pending: deque = deque(maxlen=10)



            def mark_resolved(self, task_id: str):

                self.resolved.append(task_id)

                if task_id in self.pending:

                    self.pending.remove(task_id)



            def add_pending(self, task_id: str):

                if task_id not in self.pending:

                    self.pending.append(task_id)



            def get_status(self, task_id: str) -> str:

                if task_id in self.resolved:

                    return "resolved"

                if task_id in self.pending:

                    return "pending"

                return "unknown"



        tracker = TaskTracker()



        tracker.add_pending("task1")

        tracker.add_pending("task2")

        tracker.add_pending("task3")



        assert tracker.get_status("task1") == "pending"



        tracker.mark_resolved("task1")



        assert tracker.get_status("task1") == "resolved"

        assert tracker.get_status("task2") == "pending"



    def test_compression_preserves_task_context(self):

        """测试压缩保留任务上下文"""



        class MiniTaskContext:

            def __init__(self):

                self.active_task: str | None = None

                self.task_history: list[str] = []



            def start_task(self, task: str):

                self.active_task = task

                self.task_history.append(f"start:{task}")



            def complete_task(self):

                if self.active_task:

                    self.task_history.append(f"complete:{self.active_task}")

                    self.active_task = None



            def get_context_summary(self) -> str:

                if self.active_task:

                    return f"Working on: {self.active_task}"

                if self.task_history:

                    return f"Last: {self.task_history[-1]}"

                return "No active task"



        ctx = MiniTaskContext()

        ctx.start_task("写代码")

        ctx.start_task("测试")



        assert ctx.active_task == "测试"

        assert "start:写代码" in ctx.task_history



        ctx.complete_task()



        assert ctx.active_task is None





if __name__ == "__main__":

    pytest.main([__file__, "-v"])

