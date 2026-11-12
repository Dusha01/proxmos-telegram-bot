from __future__ import annotations

from influx.csv_parse import FluxTable

_CPU_SENSOR_PREFIXES = ("coretemp", "acpitz")
_NETWORK_SENSOR_MARKERS = ("r8169", "iwlwifi", "enp", "eth")


def _friendly_device(device: str) -> str:
    mapping = {
        "nvme0": "NVMe 0",
        "nvme1": "NVMe 1",
        "nvme0n1": "NVMe 0",
        "nvme1n1": "NVMe 1",
        "sda": "HDD sda",
        "sdb": "HDD sdb",
        "sdc": "HDD sdc",
    }
    if device in mapping:
        return mapping[device]
    if device.startswith("nvme"):
        return device.upper()
    return device


def label_disk_series_table(table: FluxTable) -> str | None:
    measurement = table.labels.get("_measurement", "")
    device = table.labels.get("device", "").strip()
    sensor = table.labels.get("sensor", "").strip()

    if measurement == "smart_device" and device:
        return _friendly_device(device)

    if measurement != "temp" or not sensor:
        return None
    if sensor.startswith(_CPU_SENSOR_PREFIXES):
        return None
    if any(marker in sensor for marker in _NETWORK_SENSOR_MARKERS):
        return None
    if sensor.startswith("nvme_sensor_"):
        return None
    if sensor == "nvme_composite":
        return "NVMe (composite)"
    if sensor.startswith("nvme_"):
        return sensor.replace("_", " ")
    return None


def is_disk_temperature_field(field: str) -> bool:
    normalized = field.lower()
    if normalized in {"exit_status", "exit_status_code"}:
        return False
    return (
        normalized == "temp_c"
        or "temp" in normalized
        or normalized
        in {
            "temperature",
            "temperature_celsius",
        }
    )


def disk_series_sort_key(label: str) -> tuple[int, str]:
    order = {
        "NVMe 0": 0,
        "NVMe 1": 1,
        "HDD sda": 2,
        "HDD sdb": 3,
        "HDD sdc": 4,
    }
    return (order.get(label, 100), label)
