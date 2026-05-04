"""

Config Management - Load from .env and environment variables

"""



from pathlib import Path

from dataclasses import dataclass, field

import os

from dotenv import load_dotenv



# Try loading .env from multiple locations (environment variables always highest priority)

# Note: Don't use override=True to ensure env variables are not overwritten by .env file

_env_loaded = False

for env_path in [

    Path(__file__).parent.parent / ".env",          # Project root .env

    Path.cwd() / ".env",                            # Current working directory .env

    Path(__file__).parent.parent.parent / ".env",   # Parent directory .env

]:

    if env_path.exists():

        load_dotenv(env_path, override=False)  # Env vars have higher priority

        _env_loaded = True



if not _env_loaded:

    load_dotenv()





@dataclass

class Config:

    """Agent Core Configuration"""



    openai_api_key: str = field(

        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")

    )

    openai_base_url: str = field(

        default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    )

    openai_model: str = field(

        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o")

    )

    notes_dir: str = field(

        default_factory=lambda: os.getenv("NOTES_DIR", str(Path.home() / "notes"))

    )



    @property

    def is_valid(self) -> bool:

        return bool(self.openai_api_key) and self.openai_api_key != "sk-your-api-key-here"



    @property

    def masked_api_key(self) -> str:

        """Masked API key for display purposes"""

        key = self.openai_api_key

        if len(key) <= 8:

            return "****"

        return key[:4] + "*" * (len(key) - 7) + key[-3:]





config = Config()

