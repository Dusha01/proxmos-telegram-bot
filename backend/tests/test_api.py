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
            mock_admins.ensure_from_env = AsyncMock()
            mock_admins.ensure_trusted_admin = AsyncMock()
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
async def test_access_ok_with_mini_app_chat_id(api_client) -> None:
    client, mock_admins = api_client
    mock_admins.find_active.return_value = AdminOut(
        user_id=1,
        chat_id=2,
        name="admin",
        active=True,
        created_at=datetime.now(UTC),
    )
    response = await client.get("/access", headers=_bot_headers(user_id=1, chat_id=2))
    assert response.status_code == 204
    mock_admins.find_active.assert_awaited_with(1, 2)


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


@pytest.mark.asyncio
@respx.mock
async def test_node_metrics(api_client) -> None:
    client, _ = api_client
    respx.get("https://pve.test:8006/api2/json/nodes/pve/status").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "node": "pve",
                    "uptime": 100,
                    "cpu": 0.2,
                    "mem": 1,
                    "maxmem": 10,
                    "disk": 1,
                    "maxdisk": 10,
                    "loadavg": [0.1, 0.2, 0.3],
                }
            },
        )
    )
    respx.get("https://pve.test:8006/api2/json/nodes/pve/rrddata").mock(
        return_value=httpx.Response(
            200,
            json={"data": [{"time": 1, "cpu": 0.2, "mem": 0.25, "temp": 40, "sda_temp": 35}]},
        )
    )
    respx.get("https://pve.test:8006/api2/json/nodes/pve/storage").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "storage": "local",
                        "type": "dir",
                        "enabled": 1,
                        "used": 1,
                        "total": 10,
                        "avail": 9,
                    }
                ]
            },
        )
    )
    response = await client.get("/node/metrics", headers=_bot_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["node"] == "pve"
    assert body["temperature_available"] is True
    assert body["disk_temperature_available"] is True
    assert len(body["disk_temperature_series"]) == 1
    assert len(body["storages"]) == 1


@pytest.mark.asyncio
@respx.mock
async def test_node_metrics_pve9_status_and_rrd(api_client) -> None:
    client, _ = api_client
    respx.get("https://pve.test:8006/api2/json/nodes/pve/status").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "uptime": 100,
                    "cpu": 0,
                    "memory": {"used": 8, "total": 10, "available": 2, "free": 2},
                    "rootfs": {"used": 1, "total": 100, "avail": 99, "free": 99},
                    "cpuinfo": {"cpus": 8},
                    "loadavg": [0.1, 0.2, 0.3],
                }
            },
        )
    )
    respx.get("https://pve.test:8006/api2/json/nodes/pve/rrddata").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "time": 1,
                        "cpu": 0.15,
                        "memused": 8,
                        "memtotal": 10,
                        "rootused": 1,
                        "roottotal": 100,
                    }
                ]
            },
        )
    )
    respx.get("https://pve.test:8006/api2/json/nodes/pve/storage").mock(
        return_value=httpx.Response(200, json={"data": []})
    )
    response = await client.get("/node/metrics", headers=_bot_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["memory_percent"] == 80.0
    assert body["cpu_percent"] == 15.0
    assert body["root_disk"]["used_percent"] == 1.0
    assert body["memory_series"]["points"][0]["value"] == 80.0


@pytest.mark.asyncio
@respx.mock
async def test_node_reboot(api_client) -> None:
    client, _ = api_client
    route = respx.post("https://pve.test:8006/api2/json/nodes/pve/status").mock(
        return_value=httpx.Response(200, json={"data": None})
    )
    response = await client.post("/node/reboot", headers=_bot_headers())
    assert response.status_code == 200
    assert route.called
