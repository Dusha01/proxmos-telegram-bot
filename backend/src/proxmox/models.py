from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

GuestKind = Literal["qemu", "lxc"]
GuestStatus = Literal["running", "stopped", "paused", "unknown"]
PowerAction = Literal["start", "stop", "shutdown", "suspend", "resume", "reboot"]


class NodeStatus(BaseModel):
    node: str
    uptime: int | None = None
    cpu: float | None = None
    maxcpu: int | None = None
    mem: int | None = None
    maxmem: int | None = None
    disk: int | None = None
    maxdisk: int | None = None
    loadavg: list[float] = Field(default_factory=list)


class Guest(BaseModel):
    vmid: int
    name: str
    kind: GuestKind
    status: GuestStatus


class GuestListResponse(BaseModel):
    items: list[Guest]
    total: int


class SummaryResponse(BaseModel):
    node: NodeStatus
    qemu_total: int
    qemu_running: int
    lxc_total: int
    lxc_running: int
