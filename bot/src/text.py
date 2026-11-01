from __future__ import annotations

PAGE_SIZE = 8

STATUS_LABELS = {
    "running": "работает",
    "stopped": "остановлен",
    "paused": "на паузе",
    "unknown": "неизвестно",
}

STATUS_POWER_LABELS = {
    "running": "включена",
    "stopped": "выключена",
    "paused": "на паузе",
    "unknown": "неизвестно",
}

ACTION_LABELS = {
    "start": "Запуск",
    "stop": "Стоп",
    "shutdown": "Выключить (ACPI)",
    "suspend": "Пауза",
    "resume": "Продолжить",
    "reboot": "Перезагрузить",
}


def format_actor_name(actor: dict | None) -> str:
    if not actor:
        return ""
    name = (actor.get("full_name") or "").strip()
    if name:
        return name
    username = actor.get("username")
    if username:
        return f"@{username}"
    user_id = actor.get("id")
    return str(user_id) if user_id is not None else ""


def format_power_notification(
    guest: dict,
    action: str,
    *,
    actor: dict | None = None,
    reached_expected: bool = True,
) -> str:
    kind = str(guest.get("kind", "?")).upper()
    vmid = guest.get("vmid", "?")
    name = guest.get("name", "")
    status = guest.get("status", "unknown")
    status_label = STATUS_LABELS.get(status, status)
    power = STATUS_POWER_LABELS.get(status, status)
    who = format_actor_name(actor)
    actor_part = f"\nИнициатор: {who}" if who else ""
    expected = _expected_status_for_action(action)

    if reached_expected and status == expected:
        if action == "start":
            detail = "успешно <b>включена</b>"
        elif action == "stop":
            detail = "успешно остановлена (<b>стоп</b>)"
        elif action == "shutdown":
            detail = "успешно <b>выключена</b>"
        elif action == "reboot":
            detail = "успешно <b>перезагружена</b>"
        elif action == "suspend":
            detail = "переведена <b>на паузу</b>"
        elif action == "resume":
            detail = "успешно <b>включена</b> (продолжение)"
        else:
            detail = ACTION_LABELS.get(action, action)
    elif not reached_expected and expected:
        detail = (
            f"команда принята, но за отведённое время статус не стал "
            f"«{STATUS_POWER_LABELS.get(expected, expected)}»"
        )
    elif action == "stop":
        detail = "выполнен <b>стоп</b> (жёсткая остановка)"
    elif action == "shutdown":
        detail = "запрошено <b>выключение (ACPI)</b>"
    else:
        detail = ACTION_LABELS.get(action, action)

    return (
        f"🔔 <b>{kind} {vmid} — {name}</b>\n"
        f"{detail}\n"
        f"Статус: {status_label} ({power})"
        f"{actor_part}"
    )


def _expected_status_for_action(action: str) -> str | None:
    mapping = {
        "start": "running",
        "stop": "stopped",
        "shutdown": "stopped",
        "reboot": "running",
        "suspend": "paused",
        "resume": "running",
    }
    return mapping.get(action)


def format_host_shutdown_notification(
    *,
    node_name: str | None = None,
    actor: dict | None = None,
) -> str:
    node = node_name or "Proxmox"
    who = format_actor_name(actor)
    actor_part = f"\nИнициатор: {who}" if who else ""
    return (
        f"🔔 <b>Хост {node}</b>\n"
        "Отправлена команда выключения ноды. Бот и API перестанут отвечать после остановки хоста."
        f"{actor_part}"
    )


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


def status_button_label(status: str) -> str:
    label = STATUS_POWER_LABELS.get(status, status)
    return f"Статус: {label}"
