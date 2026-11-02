from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("BOT_API_TOKEN", "test-bot-token")
    monkeypatch.setenv("ADMIN_USER_ID", "1")
    monkeypatch.setenv("ADMIN_CHAT_ID", "1")
    monkeypatch.setenv("MINI_APP_CHAT_ID", "2")
    monkeypatch.setenv("MONGO_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGO_DB", "proxmos_test")
    monkeypatch.setenv("PROXMOX_HOST", "https://pve.test:8006")
    monkeypatch.setenv("PROXMOX_TOKEN_ID", "user@pam!bot")
    monkeypatch.setenv("PROXMOX_TOKEN_SECRET", "secret")
    monkeypatch.setenv("PROXMOX_NODE", "pve")
    monkeypatch.setenv("PROXMOX_VERIFY_SSL", "false")
    monkeypatch.setenv("PROTECTED_GUESTS", "lxc:100")
    monkeypatch.delenv("ENV_FILE", raising=False)
    from core.settings import get_settings

    get_settings.cache_clear()
