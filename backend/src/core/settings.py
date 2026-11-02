from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.env_loader import resolve_env_file


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=resolve_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["dev", "prod"] = "dev"
    bot_api_token: str
    admin_user_id: int
    admin_chat_id: int
    mini_app_chat_id: int
    admin_name: str = ""
    mongo_url: str = "mongodb://mongo:27017"
    mongo_db: str = "proxmos_bot"

    proxmox_host: str
    proxmox_token_id: str
    proxmox_token_secret: str
    proxmox_node: str = ""
    proxmox_verify_ssl: bool = False
    protected_guests: str = ""

    @field_validator("protected_guests", mode="before")
    @classmethod
    def _strip_protected(cls, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def protected_guest_keys(self) -> frozenset[tuple[str, int]]:
        keys: set[tuple[str, int]] = set()
        for part in self.protected_guests.split(","):
            item = part.strip()
            if not item:
                continue
            kind, _, vmid_str = item.partition(":")
            if not vmid_str.isdigit():
                continue
            keys.add((kind.lower(), int(vmid_str)))
        return frozenset(keys)

    @property
    def log_level(self) -> str:
        return "DEBUG" if self.app_env == "dev" else "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
