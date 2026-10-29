from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import respx
from httpx import ASGITransport, AsyncClient

from db.models.dto import AdminOut


def _motor_mock() -> MagicMock:
    mock_collection = AsyncMock()
    mock_collection.create_index = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=mock_db)
    mock_client.close = MagicMock()
    return mock_client


@pytest.fixture
async def api_client():
    with patch("db.repositories.repo.create_motor_client", return_value=_motor_mock()):
        from api.app import create_app

        app = create_app()
        async with app.router.lifespan_context(app):
            mock_admins = AsyncMock()
            mock_admins.ensure_indexes = AsyncMock()
            mock_admins.find_active = AsyncMock(
                return_value=AdminOut(
                    user_id=1,
                    chat_id=1,
                    name="admin",
                    active=True,
                    created_at=datetime.now(UTC),
                )
            )
            mock_admins.create = AsyncMock()
            app.state.container.admins = mock_admins

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                yield client, mock_admins


def _bot_headers(user_id: int = 1, chat_id: int = 1) -> dict[str, str]:
    return {
        "X-Bot-Token": "test-bot-token",
        "X-Telegram-User-Id": str(user_id),
        "X-Telegram-Chat-Id": str(chat_id),
    }


@pytest.mark.asyncio
async def test_register_admin_without_token_returns_401(api_client) -> None:
    client, _ = api_client
    response = await client.post(
        "/admins",
        json={"user_id": 1, "chat_id": 1},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_access_wrong_user_returns_403(api_client) -> None:
    client, mock_admins = api_client
    mock_admins.find_active.return_value = None
    response = await client.get("/access", headers=_bot_headers(user_id=2, chat_id=2))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_access_ok_returns_204(api_client) -> None:
    client, _ = api_client
    response = await client.get("/access", headers=_bot_headers())
    assert response.status_code == 204


@pytest.mark.asyncio
@respx.mock
async def test_guest_action_protected_not_calling_proxmox(api_client) -> None:
    client, _ = api_client
    route = respx.post("https://pve.test:8006/api2/json/nodes/pve/lxc/100/status/stop")
    response = await client.post(
        "/guests/lxc/100/stop",
        headers=_bot_headers(),
    )
    assert response.status_code == 403
    assert route.called is False


@pytest.mark.asyncio
@respx.mock
async def test_guest_list_calls_proxmox(api_client) -> None:
    client, _ = api_client
    respx.get("https://pve.test:8006/api2/json/nodes/pve/qemu").mock(
        return_value=httpx.Response(200, json={"data": []})
    )
    response = await client.get("/guests?kind=qemu", headers=_bot_headers())
    assert response.status_code == 200
    assert response.json()["total"] == 0
