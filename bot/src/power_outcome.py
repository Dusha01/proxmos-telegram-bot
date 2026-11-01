from __future__ import annotations

import asyncio
import time
from typing import Any

from src.api.api_client import ApiClient

ACTION_EXPECTED_STATUS: dict[str, str] = {
    "start": "running",
    "stop": "stopped",
    "shutdown": "stopped",
    "reboot": "running",
    "suspend": "paused",
    "resume": "running",
}

POWER_NOTIFY_ACTIONS = frozenset(ACTION_EXPECTED_STATUS)


async def wait_for_guest_status(
    api: ApiClient,
    user_id: int,
    chat_id: int,
    kind: str,
    vmid: int,
    expected_status: str,
    *,
    timeout: float = 90.0,
    interval: float = 2.0,
) -> tuple[dict[str, Any], bool]:
    deadline = time.monotonic() + timeout
    last_guest: dict[str, Any] = {}
    while time.monotonic() < deadline:
        last_guest = await api.get_guest(user_id, chat_id, kind, vmid)
        if last_guest.get("status") == expected_status:
            return last_guest, True
        await asyncio.sleep(interval)
    if not last_guest:
        last_guest = await api.get_guest(user_id, chat_id, kind, vmid)
    return last_guest, False
