"""
�?API 提供�?�?抽象不同 LLM API 的差�?
"""

from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from typing import Optional
from agent_core.settings.settings_store import ProviderConfig
from agent_core.utils.retry import retry


from typing import Optional, TypedDict

class LLMResponse(TypedDict):
    content: str
    reasoning: str
    tool_calls: list | None


class LLMProvider:
    """统一�?LLM 提供者封�?""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                api_key=self.config.resolved_api_key(),
                base_url=self.config.base_url,
            )
        return self._client

    @property
    def model(self) -> str:
        return self.config.model

    @retry(
        max_retries=3,
        base_delay=1.0,
        max_delay=10.0,
        backoff_factor=2.0,
        retry_on_exceptions=(APIError, APIConnectionError, RateLimitError),
    )
    def chat(self, messages: list[dict], tools: list[dict] | None = None,
             tool_choice: str | None = None, temperature: float = 0.3) -> dict:
        """发送聊天请求（带重试机制）"""
        kwargs = dict(model=self.model, messages=messages, temperature=temperature)
        thinking_disabled = False
        if "deepseek" in self.config.base_url.lower():
            kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice or "auto"
        msg = self.client.chat.completions.create(**kwargs).choices[0].message
        reasoning = getattr(msg, "reasoning_content", "") or ""
        content = msg.content or ""
        
        # 获取 tool_calls（如果有�?
        tool_calls = []
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                })
        
        return {
            "content": content,
            "reasoning": reasoning,
            "tool_calls": tool_calls if tool_calls else None,
        }

    def get_embedding(self, text: str) -> list[float]:
        """获取文本 embedding（如�?API 支持�?""
        try:
            resp = self.client.embeddings.create(input=text, model="text-embedding-ada-002")
            return resp.data[0].embedding
        except Exception:
            return []

    def is_available(self) -> bool:
        """检�?API 是否可用（简�?ping�?""
        try:
            self.client.models.list()
            return True
        except Exception:
            return False

    @classmethod
    def from_config(cls, config: ProviderConfig) -> "LLMProvider":
        return cls(config)

    @classmethod
    def create_provider(cls, api_type: str, api_key: str, base_url: str,
                        model: str) -> "LLMProvider":
        """工厂方法 �?根据 api_type 创建对应提供�?""
        provider_config = ProviderConfig(
            id="custom",
            name=f"Custom {api_type}",
            api_type=api_type,
            api_key=api_key,
            base_url=base_url,
            model=model,
            is_active=True,
        )
        return cls(provider_config)


class ProviderRegistry:
    """提供者注册表 �?管理所有已配置的提供�?""

    def __init__(self):
        self._providers: dict[str, LLMProvider] = {}

    def register(self, config: ProviderConfig) -> LLMProvider:
        """注册一个提供�?""
        provider = LLMProvider(config)
        self._providers[config.id] = provider
        return provider

    def get(self, provider_id: str) -> Optional[LLMProvider]:
        return self._providers.get(provider_id)

    def remove(self, provider_id: str):
        self._providers.pop(provider_id, None)

    def reload_all(self, configs: list[ProviderConfig]):
        """从配置列表重新加载所有提供�?""
        self._providers.clear()
        for c in configs:
            self.register(c)

    def list_providers(self) -> list[dict]:
        return [
            {"id": pid, "name": p.config.name, "model": p.model,
             "api_type": p.config.api_type, "is_active": p.config.is_active}
            for pid, p in self._providers.items()
        ]


# 全局单例
registry = ProviderRegistry()
