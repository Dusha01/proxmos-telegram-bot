from __future__ import annotations

from influx.csv_parse import FluxTable
from services.disk_sensor_labels import is_disk_temperature_field, label_disk_series_table


def test_label_smart_device_by_drive() -> None:
    table = FluxTable(
        labels={"_measurement": "smart_device", "device": "nvme1", "_field": "Temperature"},
    )
    assert label_disk_series_table(table) == "NVMe 1"


def test_label_temp_nvme_composite() -> None:
    table = FluxTable(labels={"_measurement": "temp", "sensor": "nvme_composite", "_field": "temp"})
    assert label_disk_series_table(table) == "NVMe (composite)"


def test_skip_cpu_sensor() -> None:
    table = FluxTable(
        labels={"_measurement": "temp", "sensor": "coretemp_package_id_0", "_field": "temp"},
    )
    assert label_disk_series_table(table) is None


def test_disk_temperature_field_filter() -> None:
    assert is_disk_temperature_field("temp_c")
    assert is_disk_temperature_field("Temperature")
    assert is_disk_temperature_field("Temperature_Celsius")
    assert not is_disk_temperature_field("exit_status")
