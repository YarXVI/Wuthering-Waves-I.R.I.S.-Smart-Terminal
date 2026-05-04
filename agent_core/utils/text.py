"""
Text utilities for string processing
"""

import re
from typing import Optional


def strip_emoji(text: str) -> str:
    """Remove emoji characters from text"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max length with suffix"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_whitespace(text: str) -> str:
    """Clean excessive whitespace from text"""
    return re.sub(r'\s+', ' ', text).strip()


def extract_code_blocks(text: str) -> list[str]:
    """Extract code blocks from markdown text"""
    pattern = r'```[\w]*\n?(.*?)```'
    return re.findall(pattern, text, re.DOTALL)


def count_words(text: str) -> int:
    """Count words in text"""
    return len(re.findall(r'\w+', text))


def remove_markdown(text: str) -> str:
    """Remove basic markdown formatting"""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    text = re.sub(r'~~(.+?)~~', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    return text


def sanitize_messages(messages: list) -> list:
    """Sanitize message content for display"""
    sanitized = []
    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get('content', '')
            sanitized.append({
                **msg,
                'content': remove_markdown(strip_emoji(content))
            })
    return sanitized


def mask_api_keys_in_dict(data: dict) -> dict:
    """Mask API keys in dictionary values"""
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = mask_api_keys_in_dict(value)
        elif isinstance(value, list):
            result[key] = [
                mask_api_keys_in_dict(item) if isinstance(item, dict) else item
                for item in value
            ]
        elif isinstance(value, str):
            # Mask API keys - look for common patterns
            masked = value
            # Check for OpenAI-style keys (sk-...)
            masked = re.sub(r'sk-[A-Za-z0-9_-]+', 'sk-***', masked)
            # Check for API keys in general
            masked = re.sub(r'api[_-]?key[\s:=]+[A-Za-z0-9_-]+', 'api_key=***', masked, flags=re.IGNORECASE)
            result[key] = masked
        else:
            result[key] = value
    return result
