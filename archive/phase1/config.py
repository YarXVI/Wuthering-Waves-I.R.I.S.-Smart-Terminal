"""
配置管理 — 从 .env 和环境变量加载
"""

from pathlib import Path
from dataclasses import dataclass, field
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Agent 核心配置"""

    # OpenAI
    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    openai_base_url: str = field(
        default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    )
    openai_model: str = field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o")
    )

    # 本地笔记目录
    notes_dir: str = field(
        default_factory=lambda: os.getenv("NOTES_DIR", str(Path.home() / "notes"))
    )

    @property
    def is_valid(self) -> bool:
        return bool(self.openai_api_key) and self.openai_api_key != "sk-your-api-key-here"


# 全局单例
config = Config()
