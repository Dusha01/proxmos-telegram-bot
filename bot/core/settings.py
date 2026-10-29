from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_file() -> str | None:
    env_file = os.getenv("ENV_FILE", ".env.dev")
    path = Path(env_file)
    if path.is_file():
        return str(path.resolve())
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
