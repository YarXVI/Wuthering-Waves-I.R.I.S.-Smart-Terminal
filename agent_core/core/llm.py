"""
LLM Client - Interface to language model APIs
"""

import os
from typing import Optional


class LLMClient:
    """Simple LLM client for chat completions"""

    def __init__(self, model: str = "gpt-4o", api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    def chat(self, messages: list[dict]) -> str:
        """
        Send chat completion request
        messages: list of {"role": "system"|"user"|"assistant", "content": str}
        Returns: assistant's response text
        """
        # Placeholder - actual implementation would call OpenAI API
        if not self.api_key:
            return "Error: No API key configured"

        user_message = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        return f"Echo: {user_message}"

    def count_tokens(self, text: str) -> int:
        """Estimate token count"""
        return len(text.split())
