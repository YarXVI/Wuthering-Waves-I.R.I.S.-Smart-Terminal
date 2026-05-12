"""Provider router for LLM selection."""

from dataclasses import dataclass
from typing import Any, Optional

try:
    from agent_core.core.llm_provider import LLMProvider, OpenAICompatibleProvider
except ImportError:
    from abc import ABC, abstractmethod

    class LLMProvider(ABC):
        @abstractmethod
        def chat(self, messages: list[dict], **kwargs: Any) -> Any:
            pass

        @abstractmethod
        def chat_stream(self, messages: list[dict], **kwargs: Any) -> Any:
            pass

    class OpenAICompatibleProvider(LLMProvider):
        def __init__(self, model: str = "gpt-4o", api_key: Optional[str] = None,
                     base_url: Optional[str] = None, timeout: float = 120.0, **kwargs):
            self._model = model
            self._api_key = api_key or ""
            self._base_url = base_url or "https://api.openai.com/v1"
            self._timeout = timeout

        def chat(self, messages: list[dict], **kwargs: Any) -> Any:
            raise NotImplementedError("OpenAICompatibleProvider chat not implemented")

        def chat_stream(self, messages: list[dict], **kwargs: Any) -> Any:
            raise NotImplementedError("OpenAICompatibleProvider chat_stream not implemented")


@dataclass
class ProviderConfig:
    """Configuration for a provider."""

    name: str
    model: str
    api_key: str
    base_url: Optional[str] = None
    timeout: int = 30
    cost_per_1k_tokens: float = 0.0
    max_context: int = 8192
    capabilities: list[str] = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = ["chat"]


class ProviderRouter:
    """Routes LLM requests to the most appropriate provider."""

    def __init__(self):
        self._providers: dict[str, LLMProvider] = {}
        self._configs: dict[str, ProviderConfig] = {}
        self._default_provider: Optional[str] = None

    def register(self, config: ProviderConfig) -> None:
        """Register a provider configuration."""
        provider = OpenAICompatibleProvider(
            model=config.model,
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
        )
        self._providers[config.name] = provider
        self._configs[config.name] = config
        if self._default_provider is None:
            self._default_provider = config.name

    async def chat(self, messages: list[dict], **kwargs) -> Any:
        """Route chat request to the best provider."""
        provider_name = self._select_provider(messages, kwargs)
        provider = self._providers.get(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")
        return await provider.chat(messages, **kwargs)

    def _select_provider(self, messages: list[dict], kwargs: dict) -> str:
        """Select the best provider for the task."""
        return self._default_provider or list(self._providers.keys())[0]

    def get_stats(self) -> dict:
        """Get provider statistics."""
        return {
            name: {
                "model": config.model,
                "cost_per_1k": config.cost_per_1k_tokens,
                "max_context": config.max_context,
                "capabilities": config.capabilities,
            }
            for name, config in self._configs.items()
        }
