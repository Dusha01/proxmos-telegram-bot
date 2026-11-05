from __future__ import annotations

from proxmox.models import MetricPoint, MetricSeries

_RRD_META_KEYS = frozenset(
    {
        "time",
        "cpu",
        "maxcpu",
        "mem",
        "maxmem",
        "loadavg",
        "netin",
        "netout",
        "diskread",
        "diskwrite",
        "iowait",
        "wait",
        "idle",
        "steal",
        "maxdisk",
        "disk",
        "swaptotal",
        "swapused",
        "swapfree",
        "ksm",
    }
)
_CPU_TEMP_KEYS = frozenset({"temp", "cputemp"})


def _disk_temp_label(key: str) -> str:
    if key.endswith("_temp"):
        return key[: -len("_temp")]
    return key


def _discover_disk_temp_keys(rows: list[dict]) -> list[str]:
    keys: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key in row:
            if key in _RRD_META_KEYS or key in _CPU_TEMP_KEYS:
                continue
            if key.endswith("_temp"):
                keys.add(key)
    return sorted(keys)


def _extract_series(
    rows: list[dict],
    value_key: str,
    *,
    scale: float = 1.0,
    label: str,
    unit: str,
) -> MetricSeries:
    points: list[MetricPoint] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        ts = row.get("time")
        raw = row.get(value_key)
        if ts is None or raw is None:
            continue
        try:
            value = float(raw) * scale
        except (TypeError, ValueError):
            continue
        points.append(MetricPoint(timestamp=int(ts), value=value))
    points.sort(key=lambda p: p.timestamp)
    return MetricSeries(label=label, unit=unit, points=points)


def map_rrd_to_load_series(rows: list[dict]) -> list[MetricSeries]:
    series: list[MetricSeries] = []
    cpu = _extract_series(rows, "cpu", scale=100.0, label="CPU", unit="%")
    if cpu.points:
        series.append(cpu)
    load = _extract_series(rows, "loadavg", scale=1.0, label="Load", unit="")
    if load.points:
        series.append(load)
    return series


def map_rrd_to_memory_series(rows: list[dict]) -> MetricSeries | None:
    mem = _extract_series(rows, "mem", scale=100.0, label="RAM", unit="%")
    if mem.points:
        return mem
    used = _extract_series(rows, "memused", scale=1.0, label="RAM used", unit="B")
    if used.points:
        return used
    return None


def map_rrd_to_temperature_series(rows: list[dict]) -> tuple[list[MetricSeries], bool]:
    for key, label in (("temp", "CPU temp"), ("cputemp", "CPU temp")):
        s = _extract_series(rows, key, scale=1.0, label=label, unit="°C")
        if s.points:
            return [s], True
    return [], False


def map_rrd_to_disk_temperature_series(rows: list[dict]) -> tuple[list[MetricSeries], bool]:
    series: list[MetricSeries] = []
    for key in _discover_disk_temp_keys(rows):
        label = _disk_temp_label(key)
        s = _extract_series(rows, key, scale=1.0, label=label, unit="°C")
        if s.points:
            series.append(s)
    return series, len(series) > 0
