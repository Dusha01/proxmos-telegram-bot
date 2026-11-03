from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.power_outcome import (
    ACTION_EXPECTED_STATUS,
    POWER_NOTIFY_ACTIONS,
    wait_for_guest_status,
)


def test_power_notify_actions_match_expected_status_keys() -> None:
    assert POWER_NOTIFY_ACTIONS == frozenset(ACTION_EXPECTED_STATUS)


@pytest.mark.asyncio
async def test_wait_for_guest_status_returns_when_status_matches() -> None:
    api = AsyncMock()
    api.get_guest = AsyncMock(
        side_effect=[
            {"status": "running", "vmid": 100},
            {"status": "stopped", "vmid": 100},
        ]
    )
    guest, ok = await wait_for_guest_status(
        api, 1, 2, "lxc", 100, "stopped", timeout=1.0, interval=0.01
    )
    assert ok is True
    assert guest["status"] == "stopped"
    assert api.get_guest.await_count == 2


@pytest.mark.asyncio
async def test_wait_for_guest_status_times_out() -> None:
    api = AsyncMock()
    api.get_guest = AsyncMock(return_value={"status": "running", "vmid": 100})

    guest, ok = await wait_for_guest_status(
        api, 1, 2, "lxc", 100, "stopped", timeout=0.05, interval=0.01
    )
    assert ok is False
    assert guest["status"] == "running"
