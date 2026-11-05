from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from influx_samples_data import SAMPLE_CPU_CSV, SAMPLE_CPU_LAST, SAMPLE_MEMORY_LAST

from core.settings import Settings
from influx.client import InfluxClient
from services.influx_metrics import InfluxMetricsService


@pytest.fixture
def influx_settings() -> Settings:
    return Settings(
        app_env="dev",
        bot_api_token="t",
        admin_user_id=1,
        admin_chat_id=1,
        mini_app_chat_id=2,
        proxmox_host="https://pve.test:8006",
        proxmox_token_id="id",
        proxmox_token_secret="secret",
        influx_url="http://influx.test:8086",
        influx_token="token",
        influx_host_tag="dusha",
    )


@pytest.mark.asyncio
async def test_fetch_cpu_percent(influx_settings: Settings) -> None:
    client = MagicMock(spec=InfluxClient)
    client.query_csv = AsyncMock(return_value=SAMPLE_CPU_LAST)
    service = InfluxMetricsService(client, influx_settings)
    value = await service.fetch_cpu_percent()
    assert value == 2.0


@pytest.mark.asyncio
async def test_fetch_load_series(influx_settings: Settings) -> None:
    client = MagicMock(spec=InfluxClient)
    client.query_csv = AsyncMock(side_effect=[SAMPLE_CPU_CSV, ""])
    service = InfluxMetricsService(client, influx_settings)
    series = await service.fetch_load_series()
    assert len(series) == 1
    assert series[0].label == "CPU"
    assert series[0].points[-1].value == 2.0


@pytest.mark.asyncio
async def test_fetch_memory_snapshot(influx_settings: Settings) -> None:
    client = MagicMock(spec=InfluxClient)
    client.query_csv = AsyncMock(
        side_effect=[
            SAMPLE_MEMORY_LAST,
            """,result,table,_start,_stop,_time,_value,_field,_measurement,host,object
,_result,0,2026-11-05T10:50:00Z,2026-11-05T11:00:00Z,2026-11-05T11:00:00Z,10000000000,memtotal,memory,dusha,nodes
""",
        ]
    )
    service = InfluxMetricsService(client, influx_settings)
    snap = await service.fetch_memory_snapshot()
    assert snap.used == 8_000_000_000
    assert snap.total == 10_000_000_000
    assert snap.used_percent == 80.0
