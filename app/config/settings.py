from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class Settings:
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-120b"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        )


settings = Settings.from_env()
