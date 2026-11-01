from __future__ import annotations

from src.text import format_power_notification


def test_format_power_notification_stop_success() -> None:
    text = format_power_notification(
        {"kind": "qemu", "vmid": 101, "name": "web", "status": "stopped"},
        "stop",
        actor={"full_name": "Admin", "username": None, "id": 1},
        reached_expected=True,
    )
    assert "QEMU 101" in text
    assert "стоп" in text
    assert "выключена" in text
    assert "Admin" in text


def test_format_power_notification_shutdown_success() -> None:
    text = format_power_notification(
        {"kind": "lxc", "vmid": 102, "name": "db", "status": "stopped"},
        "shutdown",
        reached_expected=True,
    )
    assert "LXC 102" in text
    assert "выключена" in text


def test_format_power_notification_start_success() -> None:
    text = format_power_notification(
        {"kind": "qemu", "vmid": 101, "name": "web", "status": "running"},
        "start",
        reached_expected=True,
    )
    assert "включена" in text


def test_format_power_notification_timeout() -> None:
    text = format_power_notification(
        {"kind": "qemu", "vmid": 101, "name": "web", "status": "running"},
        "shutdown",
        reached_expected=False,
    )
    assert "не стал" in text
