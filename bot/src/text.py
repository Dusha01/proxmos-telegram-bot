from __future__ import annotations

PAGE_SIZE = 8

STATUS_LABELS = {
    "running": "работает",
    "stopped": "остановлен",
    "paused": "на паузе",
    "unknown": "неизвестно",
}

ACTION_LABELS = {
    "start": "Запуск",
    "stop": "Стоп",
    "shutdown": "Выключение (ACPI)",
    "suspend": "Пауза",
    "resume": "Продолжить",
}


def format_bytes(value: int | None) -> str:
    if value is None:
        return "—"
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{value} B"


def format_summary(data: dict) -> str:
    node = data["node"]
    load = node.get("loadavg") or []
    load_str = ", ".join(f"{x:.2f}" for x in load[:3]) if load else "—"
    cpu_pct = ""
    if node.get("cpu") is not None:
        cpu_pct = f"{node['cpu'] * 100:.1f}%"
    mem = f"{format_bytes(node.get('mem'))} / {format_bytes(node.get('maxmem'))}"
    disk = f"{format_bytes(node.get('disk'))} / {format_bytes(node.get('maxdisk'))}"
    uptime = node.get("uptime")
    uptime_str = f"{uptime // 3600} ч" if isinstance(uptime, int) else "—"
    return (
        f"<b>Proxmox — {node.get('node', '?')}</b>\n"
        f"Uptime: {uptime_str}\n"
        f"CPU: {cpu_pct or '—'}\n"
        f"RAM: {mem}\n"
        f"Диск: {disk}\n"
        f"Load: {load_str}\n\n"
        f"QEMU: {data['qemu_running']}/{data['qemu_total']} работает\n"
        f"LXC: {data['lxc_running']}/{data['lxc_total']} работает"
    )


def format_node_detail(node: dict) -> str:
    load = node.get("loadavg") or []
    load_str = ", ".join(f"{x:.2f}" for x in load[:3]) if load else "—"
    return (
        f"<b>Хост {node.get('node', '?')}</b>\n"
        f"Load: {load_str}\n"
        f"RAM: {format_bytes(node.get('mem'))} / {format_bytes(node.get('maxmem'))}\n"
        f"Диск: {format_bytes(node.get('disk'))} / {format_bytes(node.get('maxdisk'))}\n\n"
        "Выключение хоста остановит бота и API. Включить обратно из Telegram нельзя."
    )


def format_guest(guest: dict) -> str:
    status = STATUS_LABELS.get(guest.get("status", "unknown"), guest.get("status"))
    kind = guest.get("kind", "?").upper()
    return (
        f"<b>{kind} {guest.get('vmid')} — {guest.get('name')}</b>\n"
        f"Статус: {status}"
    )


def format_guest_list_title(kind: str, page: int, total: int) -> str:
    kind_label = "QEMU" if kind == "qemu" else "LXC"
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    return f"<b>{kind_label}</b> ({total}), стр. {page + 1}/{pages}"
