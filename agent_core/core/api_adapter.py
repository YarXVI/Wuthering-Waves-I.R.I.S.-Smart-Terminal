"""

API 适配器 - 支持多种 LLM API 格式

chat_completions: OpenAI兼容端点

anthropic_messages: Anthropic原生格式

codex_responses: Codex响应API

"""



from abc import ABC, abstractmethod

from dataclasses import dataclass

from typing import Any

import json





@dataclass

class APIResponse:

    content: str

    reasoning: str = ""

    tool_calls: list | None = None

    raw_response: dict | None = None





class APIAdapter(ABC):

    """API适配器抽象基类"""



    @abstractmethod

    def format_request(self, messages: list[dict], tools: list[dict] | None = None,

                       temperature: float = 0.3, **kwargs) -> dict:

        """格式化请求数据"""

        pass



    @abstractmethod

    def parse_response(self, raw_response: Any) -> APIResponse:

        """解析响应数据"""

        pass





class ChatCompletionsAdapter(APIAdapter):

    """OpenAI Chat Completions 格式适配器"""



    def format_request(self, messages: list[dict], tools: list[dict] | None = None,

                       temperature: float = 0.3, **kwargs) -> dict:

        result = {

            "model": kwargs.get("model", "gpt-4"),

            "messages": messages,

            "temperature": temperature,

        }

        if tools:

            result["tools"] = tools

            result["tool_choice"] = kwargs.get("tool_choice", "auto")

        return result



    def parse_response(self, raw_response: Any) -> APIResponse:

        message = raw_response.choices[0].message

        content = message.content or ""

        reasoning = getattr(message, "reasoning_content", "") or ""



        tool_calls = None

        if hasattr(message, "tool_calls") and message.tool_calls:

            tool_calls = []

            for tc in message.tool_calls:

                tool_calls.append({

                    "id": tc.id,

                    "type": tc.type,

                    "function": {

                        "name": tc.function.name,

                        "arguments": tc.function.arguments,

                    }

                })



        return APIResponse(

            content=content,

            reasoning=reasoning,

            tool_calls=tool_calls,

            raw_response=raw_response.model_dump() if hasattr(raw_response, "model_dump") else None,

        )





class AnthropicMessagesAdapter(APIAdapter):

    """Anthropic Messages API 格式适配器"""



    SYSTEM_PROMPT_PREFIX = "【系统】"



    def format_request(self, messages: list[dict], tools: list[dict] | None = None,

                       temperature: float = 0.3, **kwargs) -> dict:

        anthropic_messages = []

        system_content = ""



        for msg in messages:

            role = msg["role"]

            content = msg["content"]



            if role == "system":

                system_content = content

            elif role == "user":

                anthropic_messages.append({

                    "role": "user",

                    "content": content,

                })

            elif role == "assistant":

                tc = msg.get("tool_calls")

                if tc:

                    anthropic_messages.append({

                        "role": "assistant",

                        "content": content,

                    })

                    for t in tc:

                        anthropic_messages.append({

                            "role": "user",

                            "content": f"<result>{t['function']['arguments']}</result>",

                        })

                else:

                    anthropic_messages.append({

                        "role": "assistant",

                        "content": content,

                    })



        result = {

            "model": kwargs.get("model", "claude-3-5-sonnet-20241022"),

            "messages": anthropic_messages,

            "temperature": temperature,

            "max_tokens": kwargs.get("max_tokens", 4096),

        }



        if system_content:

            result["system"] = system_content



        if tools:

            result["tools"] = self._format_tools(tools)



        return result



    def _format_tools(self, tools: list[dict]) -> list[dict]:

        """格式化工具为Anthropic格式"""

        formatted = []

        for tool in tools:

            formatted.append({

                "name": tool["name"],

                "description": tool.get("description", ""),

                "input_schema": tool.get("parameters", {}),

            })

        return formatted



    def parse_response(self, raw_response: Any) -> APIResponse:

        content = ""

        reasoning = ""

        tool_calls = None



        if hasattr(raw_response, "content"):

            for block in raw_response.content:

                if hasattr(block, "type"):

                    if block.type == "text":

                        content = block.text

                    elif block.type == "thinking":

                        reasoning = getattr(block, "thinking", "") or ""



        stop_reason = raw_response.stop_reason if hasattr(raw_response, "stop_reason") else None

        if stop_reason == "tool_use":

            tool_calls = []

            for block in raw_response.content:

                if hasattr(block, "type") and block.type == "tool_use":

                    tool_calls.append({

                        "id": block.id,

                        "type": "function",

                        "function": {

                            "name": block.name,

                            "arguments": json.dumps(block.input),

                        }

                    })



        return APIResponse(

            content=content,

            reasoning=reasoning,

            tool_calls=tool_calls,

            raw_response=raw_response.model_dump() if hasattr(raw_response, "model_dump") else None,

        )





class CodexResponsesAdapter(APIAdapter):

    """OpenAI Codex Responses API 格式适配器"""



    def format_request(self, messages: list[dict], tools: list[dict] | None = None,

                       temperature: float = 0.3, **kwargs) -> dict:

        last_message = messages[-1] if messages else {}



        result = {

            "model": kwargs.get("model", "gpt-4o"),

            "input": last_message.get("content", ""),

            "temperature": temperature,

        }



        if tools:

            result["tools"] = tools



        return result



    def parse_response(self, raw_response: Any) -> APIResponse:

        content = ""

        if hasattr(raw_response, "output") and raw_response.output:

            content = raw_response.output



        return APIResponse(

            content=content,

            reasoning="",

            tool_calls=None,

            raw_response=raw_response.model_dump() if hasattr(raw_response, "model_dump") else None,

        )





class APIAdapterFactory:

    """API适配器工厂"""



    _adapters = {

        "chat_completions": ChatCompletionsAdapter,

        "anthropic_messages": AnthropicMessagesAdapter,

        "codex_responses": CodexResponsesAdapter,

    }



    @classmethod

    def get_adapter(cls, api_mode: str) -> APIAdapter:

        adapter_class = cls._adapters.get(api_mode, ChatCompletionsAdapter)

        return adapter_class()



    @classmethod

    def register_adapter(cls, name: str, adapter_class: type[APIAdapter]):

        """注册新的适配器"""

        cls._adapters[name] = adapter_class





class APIModeRouter:

    """API模式路由器 - 根据关键词自动选择合适的API模式"""



    def __init__(self, default_mode: str = "chat_completions"):

        self.default_mode = default_mode

        self._route_rules: list[tuple[callable, str]] = []



    def add_rule(self, condition: callable, api_mode: str):

        """添加路由规则



        Args:

            condition: 返回True时使用该api_mode

            api_mode: API模式名称

        """

        self._route_rules.append((condition, api_mode))



    def route(self, messages: list[dict], context: dict | None = None) -> str:

        """根据消息和上下文选择API模式"""

        context = context or {}



        for condition, api_mode in self._route_rules:

            try:

                if condition(messages, context):

                    return api_mode

            except Exception:

                continue



        return self.default_mode





def create_default_router() -> APIModeRouter:

    """创建默认路由器"""

    router = APIModeRouter(default_mode="chat_completions")



    router.add_rule(

        lambda m, c: c.get("provider", "").lower() == "anthropic",

        "anthropic_messages"

    )

    router.add_rule(

        lambda m, c: c.get("provider", "").lower() == "openai" and c.get("is_codex", False),

        "codex_responses"

    )



    return router

