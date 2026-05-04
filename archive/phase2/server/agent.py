"""Agent 运行时"""
from server.core.llm import LLMClient
from server.tools.file_ops import search_local_files, read_file_content, SEARCH_TOOL, READER_TOOL

SYSTEM_PROMPT = """你是一个智能工作助手，名叫"爱弥斯"。

## 你的角色
你是一个驻场 AI 助手，像办公室员工一样工作。

## 可用工具
- search_local_files：在本地文件中搜索关键词
- read_file_content：读取指定文件的完整内容

## 工作方式
1. 理解用户的真正需求，信息不够就追问
2. 需要资料时使用工具搜索和读取本地文件
3. 给出清晰、结构化、有价值的回答
4. 标注信息来源

## 输出要求
- 结构化：使用标题、列表组织内容
- 诚实：找不到就说找不到
- 不使用表情符号
"""


class Agent:
    def __init__(self):
        self.llm = LLMClient()
        self.messages: list[dict] = []
        self.tools = [SEARCH_TOOL, READER_TOOL]
        self.tool_handlers = {
            "search_local_files": search_local_files,
            "read_file_content": read_file_content,
        }

    def reset(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def run(self, user_input: str) -> str:
        if not self.messages:
            self.reset()
        self.messages.append({"role": "user", "content": user_input})
        result = self.llm.chat_with_tools(self.messages, self.tools, self.tool_handlers)
        self.messages.append({"role": "assistant", "content": result})
        return result
