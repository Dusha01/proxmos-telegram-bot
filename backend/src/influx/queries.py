from __future__ import annotations


def _node_cpustat_filter(host: str, field: str) -> str:
    return (
        f'r._measurement == "cpustat" and r.host == "{host}" '
        f'and r.object == "nodes" and r._field == "{field}"'
    )


def _node_memory_filter(host: str, field: str) -> str:
    return (
        f'r._measurement == "memory" and r.host == "{host}" '
        f'and r.object == "nodes" and r._field == "{field}"'
    )


def cpu_percent_series(*, bucket: str, host: str) -> str:
    filt = _node_cpustat_filter(host, "cpu")
    return f"""
from(bucket: "{bucket}")
  |> range(start: -1h)
  |> filter(fn: (r) => {filt})
  |> map(fn: (r) => ({{ r with _value: r._value * 100.0 }}))
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
""".strip()


def load_avg_series(*, bucket: str, host: str) -> str:
    filt = _node_cpustat_filter(host, "avg1")
    return f"""
from(bucket: "{bucket}")
  |> range(start: -1h)
  |> filter(fn: (r) => {filt})
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
""".strip()


def memory_ratio_series(*, bucket: str, host: str) -> str:
    used_filter = _node_memory_filter(host, "memused")
    total_filter = _node_memory_filter(host, "memtotal")
    return f"""
used = from(bucket: "{bucket}")
  |> range(start: -1h)
  |> filter(fn: (r) => {used_filter})
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
  |> rename(columns: {{_value: "memused"}})

total = from(bucket: "{bucket}")
  |> range(start: -1h)
  |> filter(fn: (r) => {total_filter})
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
  |> rename(columns: {{_value: "memtotal"}})

join(tables: {{used: used, total: total}}, on: ["_time"])
  |> map(fn: (r) => ({{ r with _value: float(v: r.memused) / float(v: r.memtotal) * 100.0 }}))
  |> keep(columns: ["_time", "_value"])
""".strip()


def memory_field_series(*, bucket: str, host: str, field: str) -> str:
    filt = _node_memory_filter(host, field)
    return f"""
from(bucket: "{bucket}")
  |> range(start: -10m)
  |> filter(fn: (r) => {filt})
  |> last()
""".strip()


def cpu_temperature_series(*, bucket: str, host: str, sensor: str) -> str:
    filt = (
        f'r._measurement == "temp" and r.host == "{host}" '
        f'and r.sensor == "{sensor}" and r._field == "temp"'
    )
    return f"""
from(bucket: "{bucket}")
  |> range(start: -1h)
  |> filter(fn: (r) => {filt})
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
""".strip()


def disk_temperature_series(*, bucket: str, host: str) -> str:
    return f"""
from(bucket: "{bucket}")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "temp" and r.host == "{host}" and r._field == "temp")
  |> filter(fn: (r) => r.sensor =~ /^nvme_/)
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
""".strip()


def cpu_percent_last(*, bucket: str, host: str) -> str:
    filt = _node_cpustat_filter(host, "cpu")
    return f"""
from(bucket: "{bucket}")
  |> range(start: -10m)
  |> filter(fn: (r) => {filt})
  |> last()
""".strip()
