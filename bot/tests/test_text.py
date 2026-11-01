from __future__ import annotations

from src.text import format_power_notification


def test_format_power_notification_stop() -> None:
    text = format_power_notification(
        {"kind": "qemu", "vmid": 101, "name": "web", "status": "stopped"},
        "stop",
        actor={"full_name": "Admin", "username": None, "id": 1},
    )
    assert "QEMU 101" in text
    assert "стоп" in text
    assert "остановлен" in text
    assert "Admin" in text


def test_format_power_notification_shutdown() -> None:
    text = format_power_notification(
        {"kind": "lxc", "vmid": 102, "name": "db", "status": "stopped"},
        "shutdown",
    )
    assert "LXC 102" in text
    assert "ACPI" in text
