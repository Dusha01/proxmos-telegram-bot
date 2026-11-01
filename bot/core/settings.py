from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

_BOT_ROOT = Path(__file__).resolve().parents[1]


def _resolve_env_file() -> str | None:
    override = os.getenv("ENV_FILE")
    if override:
        path = Path(override).expanduser()
        if not path.is_absolute():
            path = (_BOT_ROOT / path).resolve()
        if path.is_file():
            return str(path)
        return None
    for name in (".env.dev", ".env.prod"):
        candidate = _BOT_ROOT / name
        if candidate.is_file():
            return str(candidate)
    return None


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_resolve_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["dev", "prod"] = "dev"
    telegram_bot_token: str
    telegram_proxy_url: str = ""
    api_base_url: str = "http://api:8000"
    bot_api_token: str

    @property
    def log_level(self) -> str:
        return "DEBUG" if self.app_env == "dev" else "INFO"


@lru_cache
def get_settings() -> BotSettings:
    return BotSettings()
