from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DEMO_DIR = PROJECT_ROOT / "demo"


@dataclass
class AppConfig:
    gemini_api_key: str | None
    gemini_model: str
    gemini_temperature: float

    @property
    def llm_enabled(self) -> bool:
        return bool(self.gemini_api_key)


def load_config() -> AppConfig:
    load_dotenv()
    return AppConfig(
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        gemini_temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.2")),
    )
