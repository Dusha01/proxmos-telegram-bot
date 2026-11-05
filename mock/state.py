from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Literal

GuestKind = Literal["qemu", "lxc"]
PowerAction = Literal["start", "stop", "shutdown", "suspend", "resume", "reboot"]

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "cluster.json"

_ACTION_TO_STATUS: dict[PowerAction, str] = {
    "start": "running",
    "resume": "running",
    "stop": "stopped",
    "shutdown": "stopped",
    "suspend": "paused",
    "reboot": "running",
}


class MockStateError(Exception):
    pass


class ClusterState:
    def __init__(self, data: dict[str, Any]) -> None:
        self._snapshot = data
        self._node: str = str(data["node"])
        self._status: dict[str, Any] = copy.deepcopy(data["status"])
        self._qemu: list[dict[str, Any]] = copy.deepcopy(data.get("qemu", []))
        self._lxc: list[dict[str, Any]] = copy.deepcopy(data.get("lxc", []))
        self._storage: list[dict[str, Any]] = copy.deepcopy(data.get("storage", []))
        self._rrddata_hour: list[dict[str, Any]] = copy.deepcopy(data.get("rrddata_hour", []))

    @classmethod
    def from_fixture(cls, path: Path | None = None) -> ClusterState:
        fixture = path or FIXTURE_PATH
        with fixture.open(encoding="utf-8") as handle:
            return cls(json.load(handle))

    def reset(self) -> None:
        fresh = ClusterState.from_fixture()
        self._status = fresh._status
        self._qemu = fresh._qemu
        self._lxc = fresh._lxc
        self._storage = fresh._storage
        self._rrddata_hour = fresh._rrddata_hour

    @property
    def node_name(self) -> str:
        return self._node

    def list_nodes(self) -> list[dict[str, str]]:
        return [{"node": self._node, "status": "online"}]

    def node_status(self) -> dict[str, Any]:
        payload = copy.deepcopy(self._status)
        payload["node"] = self._node
        return payload

    def list_guests(self, kind: GuestKind) -> list[dict[str, Any]]:
        items = self._qemu if kind == "qemu" else self._lxc
        return copy.deepcopy(items)

    def apply_guest_action(self, kind: GuestKind, vmid: int, action: PowerAction) -> None:
        guests = self._qemu if kind == "qemu" else self._lxc
        guest = next((item for item in guests if int(item["vmid"]) == vmid), None)
        if guest is None:
            raise MockStateError(f"guest {kind}:{vmid} not found")
        current = str(guest.get("status", "unknown"))
        new_status = _resolve_transition(current, action)
        guest["status"] = new_status

    def list_storage(self) -> list[dict[str, Any]]:
        return copy.deepcopy(self._storage)

    def list_rrddata(self, timeframe: str) -> list[dict[str, Any]]:
        if timeframe != "hour":
            return []
        return copy.deepcopy(self._rrddata_hour)

    def record_node_shutdown(self) -> None:
        self._status["uptime"] = 0

    def record_node_reboot(self) -> None:
        self._status["uptime"] = 120


def _resolve_transition(current: str, action: PowerAction) -> str:
    target = _ACTION_TO_STATUS[action]
    if action == "start" and current == "paused":
        raise MockStateError("use resume for paused guest")
    if action == "resume" and current != "paused":
        raise MockStateError(f"resume from {current}")
    if action == "suspend" and current != "running":
        raise MockStateError(f"suspend from {current}")
    if action == "reboot" and current != "running":
        raise MockStateError(f"reboot from {current}")
    if action in ("stop", "shutdown") and current == "stopped":
        return "stopped"
    if action in ("start", "resume") and current == "running":
        return "running"
    return target
