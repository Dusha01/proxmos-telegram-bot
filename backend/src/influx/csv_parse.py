from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FluxTable:
    labels: dict[str, str] = field(default_factory=dict)
    points: list[tuple[int, float]] = field(default_factory=list)


def _parse_time(raw: str) -> int | None:
    text = raw.strip()
    if not text:
        return None
    if text.isdigit():
        return int(text)
    try:
        normalized = text.replace("Z", "+00:00")
        return int(datetime.fromisoformat(normalized).timestamp())
    except ValueError:
        return None


def _parse_value(raw: str) -> float | None:
    text = raw.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_annotated_csv(csv_text: str) -> list[FluxTable]:
    if not csv_text.strip():
        return []
    tables: list[FluxTable] = []
    header: list[str] = []
    for row in csv.reader(io.StringIO(csv_text)):
        if not row or len(row) < 2:
            continue
        if row[1] == "result":
            header = row
            continue
        if row[1] != "_result" or not header:
            continue
        record = dict(zip(header, row, strict=False))
        if "_time" not in record or "_value" not in record:
            continue
        ts = _parse_time(record["_time"])
        value = _parse_value(record["_value"])
        if ts is None or value is None:
            continue
        label_keys = (
            "result",
            "table",
            "_start",
            "_stop",
            "_time",
            "_value",
        )
        labels = {k: v for k, v in record.items() if k not in label_keys}
        table_key = "|".join(f"{k}={labels.get(k, '')}" for k in sorted(labels))
        if not tables or tables[-1].labels.get("_key") != table_key:
            store = dict(labels)
            store["_key"] = table_key
            tables.append(FluxTable(labels=store))
        tables[-1].points.append((ts, value))
    return tables


def series_label_from_table(table: FluxTable) -> str:
    sensor = table.labels.get("sensor")
    if sensor:
        return sensor.replace("_", " ")
    field_name = table.labels.get("_field", "value")
    measurement = table.labels.get("_measurement", "metric")
    return f"{measurement}:{field_name}"
