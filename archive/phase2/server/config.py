"""闁板秶鐤嗙粻锛勬倞"""
from pathlib import Path
from dataclasses import dataclass, field
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o"))
    notes_dir: str = field(default_factory=lambda: os.getenv("NOTES_DIR", str(Path.home() / "notes")))
    host: str = field(default_factory=lambda: os.getenv("HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8765")))

    @property
    def is_valid(self) -> bool:
        return bool(self.openai_api_key) and self.openai_api_key != "sk-your-api-key-here"


config = Config()
