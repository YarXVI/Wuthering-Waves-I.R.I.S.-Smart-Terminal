"""
LLM 封装 — 统一 OpenAI API 调用入口
"""

import json
from typing import Callable
from openai import OpenAI
from config import config


class LLMClient:
    """OpenAI API 客户端封装，支持 function calling"""

    def __init__(self):
        self.client = OpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
        )
        self.model = config.openai_model

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        tool_choice: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        """
        发送对话，返回 AI 回复文本。
        如果 AI 调用了工具，返回工具调用信息（由调用方处理）。
        """
        kwargs = dict(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice or "auto"

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message

    def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        tool_handlers: dict[str, Callable],
        max_turns: int = 10,
    ) -> str:
        """
        带 function calling 的多轮对话循环。

        - messages: 对话历史（调用方维护）
        - tools: OpenAI tools 定义列表
        - tool_handlers: {tool_name: handler_fn}，handler 接收参数字典，返回字符串
        - max_turns: 最大工具调用轮次
        返回最终回答文本。
        """
        for turn in range(max_turns):
            message = self.chat(messages, tools=tools)

            if not message.tool_calls:
                # AI 直接回答了，结束
                return message.content or ""

            # 有工具调用 — 追加 AI 的响应
            messages.append(message)

            for tc in message.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)

                handler = tool_handlers.get(fn_name)
                if not handler:
                    result = f"错误：未知工具 '{fn_name}'"
                else:
                    try:
                        result = handler(**fn_args)
                    except Exception as e:
                        result = f"工具执行出错: {e}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        # 超过最大轮次，强制要求 AI 总结
        messages.append({
            "role": "user",
            "content": "请基于已有信息，给出最终回答。"
        })
        final = self.chat(messages)
        return final.content or ""
