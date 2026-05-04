"""LLM 封装 — OpenAI API"""
import json
from typing import Callable
from openai import OpenAI
from server.config import config


class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=config.openai_api_key, base_url=config.openai_base_url)
        self.model = config.openai_model

    def chat_with_tools(self, messages: list[dict], tools: list[dict], tool_handlers: dict[str, Callable], max_turns: int = 10) -> str:
        for turn in range(max_turns):
            kwargs = dict(model=self.model, messages=messages, temperature=0.3)
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message

            if not message.tool_calls:
                return message.content or ""

            messages.append(message)
            for tc in message.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)
                handler = tool_handlers.get(fn_name)
                try:
                    result = handler(**fn_args) if handler else f"未知工具: {fn_name}"
                except Exception as e:
                    result = f"工具出错: {e}"
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

        messages.append({"role": "user", "content": "请给出最终回答。"})
        final = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.3)
        return final.choices[0].message.content or ""
