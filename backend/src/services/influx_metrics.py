from __future__ import annotations

import asyncio
from dataclasses import dataclass

from core.settings import Settings
from influx.client import InfluxClient
from influx.csv_parse import parse_annotated_csv
from influx.queries import (
    cpu_percent_last,
    cpu_percent_series,
    cpu_temperature_series,
    disk_temperature_series,
    load_avg_series,
    memory_field_series,
    memory_ratio_series,
    smart_disk_temperature_series,
)
from proxmox.models import MetricPoint, MetricSeries
from services.disk_sensor_labels import (
    disk_series_sort_key,
    is_disk_temperature_field,
    label_disk_series_table,
)


@dataclass
class InfluxMemorySnapshot:
    used: int | None
    total: int | None
    used_percent: float | None


class InfluxMetricsService:
    CPU_TEMP_SENSOR = "coretemp_package_id_0"

    def __init__(self, client: InfluxClient, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    @property
    def _host(self) -> str:
        tag = self._settings.influx_host_tag.strip()
        if tag:
            return tag
        node = self._settings.proxmox_node.strip()
        if node:
            return node
        return "pve"

    def _bucket_proxmox(self) -> str:
        return self._settings.influx_bucket_proxmox

    def _bucket_hardware(self) -> str:
        return self._settings.influx_bucket_hardware

    async def fetch_load_series(self) -> list[MetricSeries]:
        host = self._host
        bucket = self._bucket_proxmox()
        cpu_csv, load_csv = await asyncio.gather(
            self._client.query_csv(cpu_percent_series(bucket=bucket, host=host)),
            self._client.query_csv(load_avg_series(bucket=bucket, host=host)),
        )
        series: list[MetricSeries] = []
        cpu = self._single_series(cpu_csv, label="CPU", unit="%")
        if cpu.points:
            series.append(cpu)
        load = self._single_series(load_csv, label="Load", unit="")
        if load.points:
            series.append(load)
        return series

    async def fetch_cpu_percent(self) -> float | None:
        host = self._host
        bucket = self._bucket_proxmox()
        csv_text = await self._client.query_csv(cpu_percent_last(bucket=bucket, host=host))
        tables = parse_annotated_csv(csv_text)
        if not tables or not tables[0].points:
            return None
        return round(tables[0].points[-1][1] * 100.0, 1)

    async def fetch_memory_series(self) -> MetricSeries | None:
        host = self._host
        bucket = self._bucket_proxmox()
        csv_text = await self._client.query_csv(memory_ratio_series(bucket=bucket, host=host))
        series = self._single_series(csv_text, label="RAM", unit="%")
        return series if series.points else None

    async def fetch_memory_snapshot(self) -> InfluxMemorySnapshot:
        host = self._host
        bucket = self._bucket_proxmox()
        used_csv = await self._client.query_csv(
            memory_field_series(bucket=bucket, host=host, field="memused")
        )
        total_csv = await self._client.query_csv(
            memory_field_series(bucket=bucket, host=host, field="memtotal")
        )
        used = self._last_int(used_csv)
        total = self._last_int(total_csv)
        percent: float | None = None
        if used is not None and total is not None and total > 0:
            percent = round(used / total * 100.0, 1)
        return InfluxMemorySnapshot(used=used, total=total, used_percent=percent)

    async def fetch_cpu_temperature_series(self) -> list[MetricSeries]:
        host = self._host
        bucket = self._bucket_hardware()
        csv_text = await self._client.query_csv(
            cpu_temperature_series(
                bucket=bucket,
                host=host,
                sensor=self.CPU_TEMP_SENSOR,
            )
        )
        series = self._single_series(csv_text, label="CPU temp", unit="°C")
        return [series] if series.points else []

    async def fetch_disk_temperature_series(self) -> list[MetricSeries]:
        host = self._host
        bucket = self._bucket_hardware()
        smart_csv = await self._client.query_csv(
            smart_disk_temperature_series(bucket=bucket, host=host)
        )
        merged: dict[str, MetricSeries] = {}
        for table in parse_annotated_csv(smart_csv):
            field = table.labels.get("_field", "")
            if not is_disk_temperature_field(field):
                continue
            label = label_disk_series_table(table)
            if label is None or not table.points:
                continue
            merged[label] = self._series_from_table(table, label=label, unit="°C")

        if merged:
            return sorted(merged.values(), key=lambda item: disk_series_sort_key(item.label))

        temp_csv = await self._client.query_csv(disk_temperature_series(bucket=bucket, host=host))
        for table in parse_annotated_csv(temp_csv):
            label = label_disk_series_table(table)
            if label is None or not table.points:
                continue
            if label == "NVMe (composite)":
                continue
            merged[label] = self._series_from_table(table, label=label, unit="°C")
        return sorted(merged.values(), key=lambda item: disk_series_sort_key(item.label))

    def _series_from_table(self, table, *, label: str, unit: str) -> MetricSeries:
        points = [
            MetricPoint(timestamp=ts, value=round(value, 1))
            for ts, value in sorted(table.points, key=lambda item: item[0])
        ]
        return MetricSeries(label=label, unit=unit, points=points)

    def _single_series(self, csv_text: str, *, label: str, unit: str) -> MetricSeries:
        tables = parse_annotated_csv(csv_text)
        if not tables:
            return MetricSeries(label=label, unit=unit, points=[])
        points = [
            MetricPoint(timestamp=ts, value=round(value, 2))
            for ts, value in sorted(tables[0].points, key=lambda item: item[0])
        ]
        return MetricSeries(label=label, unit=unit, points=points)

    def _multi_series(self, csv_text: str, *, unit: str) -> list[MetricSeries]:
        result: list[MetricSeries] = []
        for table in parse_annotated_csv(csv_text):
            if not table.points:
                continue
            label = table.labels.get("sensor") or table.labels.get("_field", "value")
            result.append(self._series_from_table(table, label=str(label), unit=unit))
        result.sort(key=lambda item: item.label)
        return result

    @staticmethod
    def _last_int(csv_text: str) -> int | None:
        tables = parse_annotated_csv(csv_text)
        if not tables or not tables[0].points:
            return None
        return int(tables[0].points[-1][1])
