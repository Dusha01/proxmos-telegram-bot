from __future__ import annotations

from services.rrd_mapping import (
    map_rrd_to_disk_temperature_series,
    map_rrd_to_load_series,
    map_rrd_to_memory_series,
    map_rrd_to_temperature_series,
)


def test_map_rrd_load_and_memory() -> None:
    rows = [
        {"time": 1, "cpu": 0.2, "loadavg": 0.5, "mem": 0.30},
        {"time": 2, "cpu": 0.25, "loadavg": 0.6, "mem": 0.31},
    ]
    load = map_rrd_to_load_series(rows)
    assert len(load) == 2
    assert load[0].points[0].value == 20.0
    mem = map_rrd_to_memory_series(rows)
    assert mem is not None
    assert mem.points[-1].value == 31.0


def test_map_rrd_temperature_optional() -> None:
    rows = [{"time": 1, "cpu": 0.1}]
    series, available = map_rrd_to_temperature_series(rows)
    assert available is False
    assert series == []

    rows_temp = [{"time": 1, "temp": 55.0}]
    series, available = map_rrd_to_temperature_series(rows_temp)
    assert available is True
    assert series[0].points[0].value == 55.0


def test_map_rrd_disk_temperature_series() -> None:
    rows = [
        {"time": 1, "sda_temp": 40.0, "nvme0n1_temp": 45.0},
        {"time": 2, "sda_temp": 41.0, "nvme0n1_temp": 46.0},
    ]
    series, available = map_rrd_to_disk_temperature_series(rows)
    assert available is True
    assert [s.label for s in series] == ["nvme0n1", "sda"]
    assert series[0].points[-1].value == 46.0
