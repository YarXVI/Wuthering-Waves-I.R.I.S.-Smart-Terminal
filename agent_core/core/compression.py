"""

上下文压缩模块 - 管理对话历史的自动压缩

保留关键信息（系统身份、用户偏好、正在执行的任务）

支持 LLM 辅助摘要

"""



from dataclasses import dataclass, field

from enum import Enum

from typing import TYPE_CHECKING

import json



if TYPE_CHECKING:

    from agent_core.core.llm import LLMClient





class MessageState(str, Enum):

    """消息状态枚举"""

    PENDING = "pending"     # 待处理/执行中

    RESOLVED = "resolved"   # 已完成/已解决

    ABANDONED = "abandoned" # 已放弃/跳过





@dataclass

class CriticalInfo:

    """关键信息标记"""

    key: str                    # 信息类型标识

    value: str                  # 信息内容

    preserved: bool = True      # 是否在压缩后保留

    priority: int = 0           # 优先级，数值越大越重要





@dataclass

class Message:

    """消息结构"""

    role: str

    content: str

    state: MessageState = MessageState.PENDING

    critical_keys: list[str] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)





@dataclass

class CompressionResult:

    """压缩结果"""

    original_count: int

    compressed_count: int

    preserved_critical_info: list[CriticalInfo]

    discarded_count: int

    summary: str = ""





class CompressionEngine:

    """上下文压缩引擎"""



    def __init__(

        self,

        max_tokens: int = 4000,

        head_protection_count: int = 2,

        tail_protection_count: int = 2,

    ):

        self.max_tokens = max_tokens

        self.head_protection_count = head_protection_count

        self.tail_protection_count = tail_protection_count

        self._llm_client: "LLMClient | None" = None



    def set_llm_client(self, client: "LLMClient"):

        """设置 LLM 客户端用于摘要生成"""

        self._llm_client = client



    def estimate_tokens(self, text: str) -> int:

        """简单估算 token 数（中文约 2 字符 = 1 token）"""

        return len(text) // 2



    def compress(

        self,

        messages: list[dict],

        critical_info: list[CriticalInfo] | None = None,

    ) -> tuple[list[dict], list[CriticalInfo]]:

        """

        压缩消息列表，保留关键信息



        Args:

            messages: 原始消息列表

            critical_info: 需要保留的关键信息列表



        Returns:

            (compressed_messages, preserved_critical_info)

        """

        if critical_info is None:

            critical_info = []



        critical_info = [ci for ci in critical_info if ci.preserved]



        if len(messages) <= self.head_protection_count + self.tail_protection_count:

            return messages, critical_info



        total_tokens = sum(self.estimate_tokens(m.get("content", "")) for m in messages)

        if total_tokens <= self.max_tokens:

            return messages, critical_info



        head = messages[:self.head_protection_count]

        tail = messages[-self.tail_protection_count:]

        middle = messages[self.head_protection_count:-self.tail_protection_count]



        compressed_middle = self._compress_middle(middle, critical_info)

        preserved = self._filter_preserved_critical_info(critical_info, head + compressed_middle + tail)



        return head + compressed_middle + tail, preserved



    def _compress_middle(

        self,

        middle_messages: list[dict],

        critical_info: list[CriticalInfo],

    ) -> list[dict]:

        """压缩中间消息"""

        if not middle_messages:

            return []



        total_tokens = sum(self.estimate_tokens(m.get("content", "")) for m in middle_messages)

        if total_tokens <= self.max_tokens // 2:

            return middle_messages



        if self._llm_client and len(middle_messages) > 4:

            return self._llm_summarize(middle_messages, critical_info)



        return self._naive_compress(middle_messages)



    def _naive_compress(self, messages: list[dict]) -> list[dict]:

        """简单压缩：保留每N条中的第一条"""

        if len(messages) <= 2:

            return messages



        step = max(1, len(messages) // 4)

        kept = []



        for i in range(0, len(messages), step):

            kept.append(messages[i])

            if len(kept) >= 4:

                break



        return kept



    def _llm_summarize(

        self,

        messages: list[dict],

        critical_info: list[CriticalInfo],

    ) -> list[dict]:

        """使用 LLM 生成摘要"""

        if not self._llm_client:

            return self._naive_compress(messages)



        critical_str = "\n".join(f"- {ci.key}: {ci.value}" for ci in critical_info)

        messages_content = "\n".join(

            f"[{m.get('role', 'unknown')}]: {m.get('content', '')[:100]}"

            for m in messages[:10]

        )



        prompt = f"""请总结以下对话的要点，保留关键信息：



关键信息：

{critical_str}



最近对话：

{messages_content}



请生成一段简短的摘要，保留所有关键信息和结论。"""



        try:

            response = self._llm_client.chat(

                [{"role": "user", "content": prompt}],

                temperature=0.3,

            )

            summary = response.get("content", "") if isinstance(response, dict) else str(response)



            return [{

                "role": "system",

                "content": f"[对话摘要] {summary}",

                "metadata": {"is_summary": True},

            }]

        except Exception:

            return self._naive_compress(messages)



    def _filter_preserved_critical_info(

        self,

        critical_info: list[CriticalInfo],

        preserved_messages: list[dict],

    ) -> list[CriticalInfo]:

        """过滤在压缩后仍被保留的关键信息"""

        preserved_text = " ".join(

            m.get("content", "")

            for m in preserved_messages

        )



        result = []

        for ci in critical_info:

            if ci.key in preserved_text or ci.value in preserved_text:

                result.append(ci)

            elif ci.priority > 5:

                result.append(ci)



        return result





class RoleValidator:

    """消息角色交替验证器"""



    ALLOWED_ROLES = {"system", "user", "assistant", "tool"}



    FORBIDDEN_TRANSITIONS = {

        "system": {"system"},

        "user": {"user"},

        "assistant": {"assistant"},

        "tool": {"tool", "user"},

    }



    def __init__(self):

        self.history: list[str] = []



    def add_message(self, role: str) -> None:

        """添加消息到历史"""

        self.history.append(role)



    def validate_transition(self, prev_role: str, next_role: str) -> tuple[bool, str]:

        """验证角色转换是否合法"""

        if prev_role not in self.ALLOWED_ROLES:

            return False, f"Unknown prev_role: {prev_role}"

        if next_role not in self.ALLOWED_ROLES:

            return False, f"Unknown next_role: {next_role}"



        if next_role in self.FORBIDDEN_TRANSITIONS.get(prev_role, []):

            return False, f"Forbidden transition: {prev_role} → {next_role}"



        return True, ""



    def validate_history(self) -> tuple[bool, str]:

        """验证完整历史序列"""

        errors = []



        # 检查所有角色是否有效

        for i, role in enumerate(self.history):

            if role not in self.ALLOWED_ROLES:

                errors.append(f"Invalid role at position {i}: {role}")



        # 检查角色转换

        for i in range(1, len(self.history)):

            is_valid, error = self.validate_transition(self.history[i-1], self.history[i])

            if not is_valid:

                errors.append(error)



        if errors:

            return False, "; ".join(errors)

        return True, ""



    def reset(self) -> None:

        """重置历史"""

        self.history = []



    def get_sequence_type(self) -> str:

        """获取序列类型描述"""

        if not self.history:

            return "empty"

        return " → ".join(self.history)





class IterationBudget:

    """迭代预算跟踪器"""



    def __init__(self, max_iterations: int = 10):

        self.max_iterations = max_iterations

        self.current_iteration = 0

        self.tool_call_count = 0

        self.total_tool_calls = 0



    def next_iteration(self) -> bool:

        """进入下一轮迭代，返回是否还有预算"""

        self.current_iteration += 1

        return self.current_iteration < self.max_iterations



    def record_tool_call(self) -> None:

        """记录一次工具调用"""

        self.tool_call_count += 1

        self.total_tool_calls += 1



    def reset_tool_calls(self) -> None:

        """重置单轮工具调用计数"""

        self.tool_call_count = 0



    def has_budget(self) -> bool:

        """检查是否还有迭代预算"""

        return self.current_iteration < self.max_iterations



    def get_status(self) -> dict:

        """获取当前状态"""

        return {

            "iteration": self.current_iteration,

            "max_iterations": self.max_iterations,

            "tool_calls_this_turn": self.tool_call_count,

            "total_tool_calls": self.total_tool_calls,

            "has_budget": self.has_budget(),

        }



    def force_stop(self, reason: str) -> None:

        """强制停止迭代"""

        self.current_iteration = self.max_iterations





class InterruptibleCall:

    """可中断的 API 调用封装"""



    def __init__(self):

        self._interrupted = False

        self._result = None



    def interrupt(self) -> None:

        """请求中断"""

        self._interrupted = True



    def is_interrupted(self) -> bool:

        """检查是否被中断"""

        return self._interrupted



    def set_result(self, result) -> None:

        """设置结果"""

        self._result = result



    def get_result(self):

        """获取结果"""

        return self._result





def create_critical_info_extractor() -> list[str]:

    """创建关键信息提取规则"""

    return [

        "user_name",

        "user_preference",

        "current_task",

        "task_goal",

        "project_name",

        "deadline",

        "system_identity",

        "agent_role",

    ]

