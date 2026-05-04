"""
Agent 运行时 — 核心大脑
"""

from core.llm import LLMClient
from tools.file_search import (
    search_local_files,
    read_file_content,
    FILE_SEARCH_TOOL,
    FILE_READER_TOOL,
)

# Agent 系统提示词 — 定义"虚拟员工"的角色
SYSTEM_PROMPT = """你是一个智能工作助手，名叫"爱弥斯"。

## 你的角色
你是一个驻场 AI 助手，像办公室员工一样工作。你的工位上堆满了各种文档工具。

## 可用工具
- search_local_files：在本地文件中搜索关键词，查找笔记和文档
- read_file_content：读取指定文件的完整内容

## 工作方式
1. 接到任务后，先理解用户真正想要什么
2. 如果信息不够，主动追问
3. 如果需要查阅资料，使用工具搜索和阅读本地文件
4. 整理信息后，给出清晰、结构化的回答
5. 回答时标注信息来源（文件名）

## 输出要求
- 结构化：使用标题、列表、代码块等组织内容
- 有价值：不要只罗列信息，要给出见解和建议
- 诚实：找不到就说找不到，不编造
"""


class Agent:
    """Agent 运行时 — 管理对话状态和工具调用"""

    def __init__(self):
        self.llm = LLMClient()
        self.messages: list[dict] = []

        # 工具注册
        self.tools = [
            FILE_SEARCH_TOOL,
            FILE_READER_TOOL,
        ]
        self.tool_handlers = {
            "search_local_files": search_local_files,
            "read_file_content": read_file_content,
        }

    def reset(self):
        """重置对话（新任务）"""
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

    def run(self, user_input: str) -> str:
        """
        处理用户输入，返回最终回答。
        自动管理对话上下文。
        """
        # 首次调用或需要新任务时重置
        if not self.messages:
            self.reset()

        self.messages.append({"role": "user", "content": user_input})

        result = self.llm.chat_with_tools(
            messages=self.messages,
            tools=self.tools,
            tool_handlers=self.tool_handlers,
        )

        self.messages.append({"role": "assistant", "content": result})
        return result
