from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

import app as mock_app_module
from state import ClusterState


@pytest.fixture(autouse=True)
def _reset_cluster() -> None:
    mock_app_module.state.reset()
    yield
    mock_app_module.state.reset()


@pytest.fixture
async def client():
    transport = ASGITransport(app=mock_app_module.app)
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        yield http


@pytest.mark.asyncio
async def test_list_nodes(client: AsyncClient) -> None:
    response = await client.get("/api2/json/nodes")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data == [{"node": "pve", "status": "online"}]


@pytest.mark.asyncio
async def test_list_qemu_has_mixed_statuses(client: AsyncClient) -> None:
    response = await client.get("/api2/json/nodes/pve/qemu")
    statuses = {item["status"] for item in response.json()["data"]}
    assert statuses >= {"running", "stopped", "paused"}


@pytest.mark.asyncio
async def test_stop_qemu_updates_status(client: AsyncClient) -> None:
    stop = await client.post("/api2/json/nodes/pve/qemu/101/status/stop")
    assert stop.status_code == 200
    response = await client.get("/api2/json/nodes/pve/qemu")
    guest = next(item for item in response.json()["data"] if item["vmid"] == 101)
    assert guest["status"] == "stopped"


@pytest.mark.asyncio
async def test_suspend_and_resume(client: AsyncClient) -> None:
    await client.post("/api2/json/nodes/pve/qemu/101/status/suspend")
    response = await client.get("/api2/json/nodes/pve/qemu")
    guest = next(item for item in response.json()["data"] if item["vmid"] == 101)
    assert guest["status"] == "paused"
    await client.post("/api2/json/nodes/pve/qemu/101/status/resume")
    response = await client.get("/api2/json/nodes/pve/qemu")
    guest = next(item for item in response.json()["data"] if item["vmid"] == 101)
    assert guest["status"] == "running"


@pytest.mark.asyncio
async def test_node_shutdown_sets_uptime_zero(client: AsyncClient) -> None:
    response = await client.post(
        "/api2/json/nodes/pve/status",
        json={"command": "shutdown"},
    )
    assert response.status_code == 200
    status = await client.get("/api2/json/nodes/pve/status")
    assert status.json()["data"]["uptime"] == 0


@pytest.mark.asyncio
async def test_reset_restores_fixture(client: AsyncClient) -> None:
    await client.post("/api2/json/nodes/pve/qemu/101/status/stop")
    await client.post("/mock/reset")
    response = await client.get("/api2/json/nodes/pve/qemu")
    guest = next(item for item in response.json()["data"] if item["vmid"] == 101)
    assert guest["status"] == "running"


def test_fixture_loads_lxc_100() -> None:
    cluster = ClusterState.from_fixture()
    lxc = cluster.list_guests("lxc")
    assert any(item["vmid"] == 100 for item in lxc)


@pytest.mark.asyncio
async def test_reboot_qemu_stays_running(client: AsyncClient) -> None:
    response = await client.post("/api2/json/nodes/pve/qemu/101/status/reboot")
    assert response.status_code == 200
    list_response = await client.get("/api2/json/nodes/pve/qemu")
    guest = next(item for item in list_response.json()["data"] if item["vmid"] == 101)
    assert guest["status"] == "running"


@pytest.mark.asyncio
async def test_reboot_stopped_guest_rejected(client: AsyncClient) -> None:
    await client.post("/api2/json/nodes/pve/qemu/102/status/start")
    await client.post("/api2/json/nodes/pve/qemu/102/status/stop")
    response = await client.post("/api2/json/nodes/pve/qemu/102/status/reboot")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_shutdown_lxc_updates_status(client: AsyncClient) -> None:
    response = await client.post("/api2/json/nodes/pve/lxc/110/status/shutdown")
    assert response.status_code == 200
    list_response = await client.get("/api2/json/nodes/pve/lxc")
    guest = next(item for item in list_response.json()["data"] if item["vmid"] == 110)
    assert guest["status"] == "stopped"


@pytest.mark.asyncio
async def test_list_storage(client: AsyncClient) -> None:
    response = await client.get("/api2/json/nodes/pve/storage")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 1
    assert "used" in data[0]


@pytest.mark.asyncio
async def test_rrddata_hour(client: AsyncClient) -> None:
    response = await client.get("/api2/json/nodes/pve/rrddata", params={"timeframe": "hour"})
    assert response.status_code == 200
    points = response.json()["data"]
    assert len(points) >= 2
    assert "cpu" in points[0]
    assert "sda_temp" in points[0]


@pytest.mark.asyncio
async def test_node_reboot_command(client: AsyncClient) -> None:
    response = await client.post(
        "/api2/json/nodes/pve/status",
        json={"command": "reboot"},
    )
    assert response.status_code == 200
    status = await client.get("/api2/json/nodes/pve/status")
    assert status.json()["data"]["uptime"] == 120
