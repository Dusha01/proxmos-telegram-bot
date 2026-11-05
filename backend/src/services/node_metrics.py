from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from proxmox.client import ProxmoxClient
from proxmox.models import (
    NodeHealthResponse,
    NodeMetricsResponse,
    NodeStatus,
    RootDiskUsage,
    StorageVolume,
)
from services.guard import node_from_raw
from services.rrd_mapping import (
    map_rrd_to_disk_temperature_series,
    map_rrd_to_load_series,
    map_rrd_to_memory_series,
    map_rrd_to_temperature_series,
)


def _storage_from_raw(raw: dict) -> StorageVolume | None:
    if raw.get("enabled") == 0:
        return None
    storage_id = str(raw.get("storage") or "")
    if not storage_id:
        return None
    used = int(raw.get("used") or 0)
    total = int(raw.get("total") or 0)
    avail = int(raw.get("avail") or max(total - used, 0))
    used_percent = (used / total * 100.0) if total > 0 else 0.0
    return StorageVolume(
        id=storage_id,
        name=storage_id,
        type=str(raw.get("type") or "") or None,
        used=used,
        total=total,
        avail=avail,
        used_percent=round(used_percent, 1),
    )


def _root_disk_from_status(node: NodeStatus) -> RootDiskUsage | None:
    if node.disk is None or node.maxdisk is None or node.maxdisk <= 0:
        return None
    used_percent = node.disk / node.maxdisk * 100.0
    return RootDiskUsage(
        used=node.disk,
        total=node.maxdisk,
        used_percent=round(used_percent, 1),
    )


class NodeMetricsService:
    def __init__(self, client: ProxmoxClient) -> None:
        self._client = client

    async def get_node_metrics(self) -> NodeMetricsResponse:
        status_raw, rrd_rows, storage_raw = await asyncio.gather(
            self._client.get_node_status(),
            self._client.get_node_rrddata(timeframe="hour"),
            self._client.list_node_storage(),
        )
        node = node_from_raw(status_raw)
        load_series = map_rrd_to_load_series(rrd_rows)
        memory_series = map_rrd_to_memory_series(rrd_rows)
        temperature_series, temperature_available = map_rrd_to_temperature_series(rrd_rows)
        disk_temperature_series, disk_temperature_available = map_rrd_to_disk_temperature_series(
            rrd_rows
        )

        storages: list[StorageVolume] = []
        for item in storage_raw:
            if isinstance(item, dict):
                vol = _storage_from_raw(item)
                if vol is not None:
                    storages.append(vol)

        cpu_percent = node.cpu * 100.0 if node.cpu is not None else None
        memory_percent: float | None = None
        if node.mem is not None and node.maxmem is not None and node.maxmem > 0:
            memory_percent = round(node.mem / node.maxmem * 100.0, 1)

        return NodeMetricsResponse(
            node=node.node,
            uptime=node.uptime,
            load_series=load_series,
            memory_series=memory_series,
            temperature_series=temperature_series,
            temperature_available=temperature_available,
            disk_temperature_series=disk_temperature_series,
            disk_temperature_available=disk_temperature_available,
            storages=storages,
            root_disk=_root_disk_from_status(node),
            loadavg=node.loadavg,
            cpu_percent=round(cpu_percent, 1) if cpu_percent is not None else None,
            memory_percent=memory_percent,
        )

    async def get_node_health(self) -> NodeHealthResponse:
        metrics = await self.get_node_metrics()
        warnings: list[str] = []
        if metrics.uptime is not None and metrics.uptime <= 0:
            warnings.append("Нода выключена или только что перезагружена")
        for storage in metrics.storages:
            if storage.used_percent >= 90:
                warnings.append(f"Storage {storage.name}: занято {storage.used_percent:.0f}%")
        if metrics.root_disk and metrics.root_disk.used_percent >= 90:
            warnings.append(
                f"Root disk: занято {metrics.root_disk.used_percent:.0f}%",
            )
        ok = len(warnings) == 0
        return NodeHealthResponse(
            ok=ok,
            node=metrics.node,
            uptime=metrics.uptime,
            warnings=warnings,
            checked_at=datetime.now(UTC),
        )
