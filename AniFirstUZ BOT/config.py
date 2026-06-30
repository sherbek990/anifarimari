"""
Global configuration loaded from environment variables (.env file).
"""
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv
import os

load_dotenv()


def _parse_admin_ids(raw: str) -> List[int]:
    if not raw:
        return []
    return [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: List[int] = field(default_factory=lambda: _parse_admin_ids(os.getenv("ADMIN_IDS", "")))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot.db")
    EPISODES_PER_PAGE: int = int(os.getenv("EPISODES_PER_PAGE", "20"))
    EPISODES_PER_ROW: int = 5


config = Config()

if not config.BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Please configure your .env file (see .env.example).")
