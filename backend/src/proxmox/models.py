from __future__ import annotations

from datetime import datetime
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


class MetricPoint(BaseModel):
    timestamp: int
    value: float


class MetricSeries(BaseModel):
    label: str
    unit: str = ""
    points: list[MetricPoint] = Field(default_factory=list)


class StorageVolume(BaseModel):
    id: str
    name: str
    type: str | None = None
    used: int
    total: int
    avail: int
    used_percent: float


class RootDiskUsage(BaseModel):
    used: int
    total: int
    used_percent: float


class NodeMetricsResponse(BaseModel):
    node: str
    uptime: int | None = None
    load_series: list[MetricSeries] = Field(default_factory=list)
    memory_series: MetricSeries | None = None
    temperature_series: list[MetricSeries] = Field(default_factory=list)
    temperature_available: bool = False
    disk_temperature_series: list[MetricSeries] = Field(default_factory=list)
    disk_temperature_available: bool = False
    storages: list[StorageVolume] = Field(default_factory=list)
    root_disk: RootDiskUsage | None = None
    loadavg: list[float] = Field(default_factory=list)
    cpu_percent: float | None = None
    memory_percent: float | None = None
    memory_used: int | None = None
    memory_total: int | None = None
    grafana_dashboard_url: str | None = None
    metrics_source: Literal["influx", "proxmox"] = "proxmox"


class NodeHealthResponse(BaseModel):
    ok: bool
    node: str
    uptime: int | None = None
    warnings: list[str] = Field(default_factory=list)
    checked_at: datetime
