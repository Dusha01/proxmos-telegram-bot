from __future__ import annotations

from influx_samples_data import SAMPLE_CPU_CSV, SAMPLE_MEMORY_LAST

from influx.csv_parse import parse_annotated_csv, series_label_from_table


def test_parse_cpu_csv() -> None:
    tables = parse_annotated_csv(SAMPLE_CPU_CSV)
    assert len(tables) == 1
    assert len(tables[0].points) == 2
    assert tables[0].points[0][1] == 1.5


def test_parse_memory_last() -> None:
    tables = parse_annotated_csv(SAMPLE_MEMORY_LAST)
    assert tables[0].points[-1][1] == 8_000_000_000


def test_series_label_uses_sensor() -> None:
    from influx.csv_parse import FluxTable

    table = FluxTable(labels={"sensor": "nvme_composite", "_field": "temp"})
    assert series_label_from_table(table) == "nvme composite"
