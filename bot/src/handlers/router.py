from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.api.api_client import ApiClient, ApiClientError
from src.power_outcome import ACTION_EXPECTED_STATUS, POWER_NOTIFY_ACTIONS, wait_for_guest_status
from src.text import (
    ACTION_LABELS,
    PAGE_SIZE,
    STATUS_POWER_LABELS,
    format_guest,
    format_guest_list_title,
    format_host_shutdown_notification,
    format_node_detail,
    format_power_notification,
    format_summary,
    status_button_label,
)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, api: ApiClient, user_id: int, chat_id: int) -> None:
    await _send_summary(message, api, user_id, chat_id)


@router.callback_query(F.data == "m:refresh")
async def cb_refresh(callback: CallbackQuery, api: ApiClient, user_id: int, chat_id: int) -> None:
    await callback.answer()
    if callback.message:
        await _send_summary(callback.message, api, user_id, chat_id, edit=True)


@router.callback_query(F.data == "m:host")
async def cb_host(callback: CallbackQuery, api: ApiClient, user_id: int, chat_id: int) -> None:
    await callback.answer()
    try:
        node = await api.get_node(user_id, chat_id)
    except ApiClientError as exc:
        await _reply_error(callback, str(exc))
        return
    text = format_node_detail(node)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Выключить хост…", callback_data="h:sd:1")],
            [InlineKeyboardButton(text="« Назад", callback_data="m:refresh")],
        ]
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("m:vm:"))
async def cb_list_qemu(callback: CallbackQuery, api: ApiClient, user_id: int, chat_id: int) -> None:
    page = _parse_page(callback.data, default=0)
    await _show_guest_list(callback, api, user_id, chat_id, "qemu", page)


@router.callback_query(F.data.startswith("m:lx:"))
async def cb_list_lxc(callback: CallbackQuery, api: ApiClient, user_id: int, chat_id: int) -> None:
    page = _parse_page(callback.data, default=0)
    await _show_guest_list(callback, api, user_id, chat_id, "lxc", page)


@router.callback_query(F.data.startswith("g:"))
async def cb_guest_card(
    callback: CallbackQuery, api: ApiClient, user_id: int, chat_id: int
) -> None:
    await callback.answer()
    kind, vmid = _parse_guest_ref(callback.data)
    if kind is None or vmid is None:
        return
    try:
        guest = await api.get_guest(user_id, chat_id, kind, vmid)
    except ApiClientError as exc:
        await _reply_error(callback, str(exc))
        return
    keyboard = _guest_actions_keyboard(guest)
    if callback.message:
        await callback.message.edit_text(
            format_guest(guest),
            reply_markup=keyboard,
        )


@router.callback_query(F.data.startswith("st:"))
async def cb_guest_status(
    callback: CallbackQuery,
    api: ApiClient,
    user_id: int,
    chat_id: int,
) -> None:
    kind, vmid = _parse_guest_ref(callback.data)
    if kind is None or vmid is None:
        await callback.answer("Некорректные данные")
        return
    try:
        guest = await api.get_guest(user_id, chat_id, kind, vmid)
    except ApiClientError as exc:
        await callback.answer("Ошибка", show_alert=True)
        if callback.message:
            await callback.message.answer(str(exc)[:300])
        return
    power = STATUS_POWER_LABELS.get(guest.get("status", "unknown"), guest.get("status", "unknown"))
    await callback.answer(f"Статус: {power}", show_alert=True)
    if callback.message:
        await callback.message.edit_text(
            format_guest(guest),
            reply_markup=_guest_actions_keyboard(guest),
        )


@router.callback_query(F.data.startswith("a:"))
async def cb_action_confirm(callback: CallbackQuery) -> None:
    await callback.answer()
    kind, vmid, action = _parse_action(callback.data)
    if kind is None or vmid is None or action is None:
        return
    label = ACTION_LABELS.get(action, action)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Подтвердить: {label}",
                    callback_data=f"c:{kind[0]}:{vmid}:{action}",
                )
            ],
            [InlineKeyboardButton(text="Отмена", callback_data=f"g:{kind[0]}:{vmid}")],
        ]
    )
    if callback.message:
        await callback.message.edit_text(
            f"Подтвердите действие <b>{label}</b> для {kind.upper()} {vmid}",
            reply_markup=keyboard,
        )


@router.callback_query(F.data.startswith("c:"))
async def cb_action_run(
    callback: CallbackQuery,
    api: ApiClient,
    user_id: int,
    chat_id: int,
) -> None:
    kind, vmid, action = _parse_confirm(callback.data)
    if kind is None or vmid is None or action is None:
        await callback.answer("Некорректные данные")
        return
    try:
        result = await api.guest_action(user_id, chat_id, kind, vmid, action)
    except ApiClientError as exc:
        await callback.answer("Ошибка", show_alert=True)
        if callback.message:
            await callback.message.answer(str(exc)[:300])
        return
    await callback.answer("Готово")
    if callback.message:
        actor = _actor_from_callback(callback)
        if action in POWER_NOTIFY_ACTIONS:
            expected = ACTION_EXPECTED_STATUS[action]
            try:
                guest, reached = await wait_for_guest_status(
                    api,
                    user_id,
                    chat_id,
                    kind,
                    vmid,
                    expected,
                )
            except ApiClientError as exc:
                await callback.message.answer(str(exc)[:300])
                return
            await callback.message.answer(
                format_power_notification(
                    guest,
                    action,
                    actor=actor,
                    reached_expected=reached,
                ),
            )
        else:
            guest = await api.get_guest(user_id, chat_id, kind, vmid)
            msg = result.get("message", "OK") if result else "OK"
            await callback.message.answer(msg)
        await callback.message.edit_text(
            format_guest(guest),
            reply_markup=_guest_actions_keyboard(guest),
        )


@router.callback_query(F.data == "h:sd:1")
async def cb_host_shutdown_step1(callback: CallbackQuery) -> None:
    await callback.answer()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да, выключить хост", callback_data="h:sd:2")],
            [InlineKeyboardButton(text="Отмена", callback_data="m:host")],
        ]
    )
    if callback.message:
        await callback.message.edit_text(
            "Бот и API остановятся вместе с хостом. Продолжить?",
            reply_markup=keyboard,
        )


@router.callback_query(F.data == "h:sd:2")
async def cb_host_shutdown_run(
    callback: CallbackQuery,
    api: ApiClient,
    user_id: int,
    chat_id: int,
) -> None:
    try:
        node = await api.get_node(user_id, chat_id)
    except ApiClientError:
        node = None
    try:
        result = await api.node_shutdown(user_id, chat_id)
    except ApiClientError as exc:
        await callback.answer("Ошибка", show_alert=True)
        if callback.message:
            await callback.message.answer(str(exc)[:300])
        return
    await callback.answer("Команда отправлена")
    if callback.message:
        node_name = node.get("node") if node else None
        actor = _actor_from_callback(callback)
        text = format_host_shutdown_notification(node_name=node_name, actor=actor)
        await callback.message.answer(text)
        msg = result.get("message", "OK") if result else "OK"
        await callback.message.edit_text(msg)


async def _send_summary(
    message: Message,
    api: ApiClient,
    user_id: int,
    chat_id: int,
    *,
    edit: bool = False,
) -> None:
    try:
        data = await api.get_summary(user_id, chat_id)
    except ApiClientError as exc:
        text = f"Ошибка API: {exc}"
        if edit:
            await message.edit_text(text)
        else:
            await message.answer(text)
        return
    text = format_summary(data)
    keyboard = _main_keyboard()
    if edit:
        await message.edit_text(text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)


async def _show_guest_list(
    callback: CallbackQuery,
    api: ApiClient,
    user_id: int,
    chat_id: int,
    kind: str,
    page: int,
) -> None:
    await callback.answer()
    try:
        data = await api.list_guests(user_id, chat_id, kind)
    except ApiClientError as exc:
        await _reply_error(callback, str(exc))
        return
    items = data.get("items") or []
    total = data.get("total", len(items))
    start = page * PAGE_SIZE
    chunk = items[start : start + PAGE_SIZE]
    rows: list[list[InlineKeyboardButton]] = []
    prefix = "q" if kind == "qemu" else "l"
    for guest in chunk:
        label = f"{guest['vmid']} {guest['name'][:20]}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"g:{prefix}:{guest['vmid']}")])
    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(
                text="«",
                callback_data=f"m:{'vm' if kind == 'qemu' else 'lx'}:{page - 1}",
            )
        )
    if start + PAGE_SIZE < total:
        nav.append(
            InlineKeyboardButton(
                text="»",
                callback_data=f"m:{'vm' if kind == 'qemu' else 'lx'}:{page + 1}",
            )
        )
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(text="« Меню", callback_data="m:refresh")])
    text = format_guest_list_title(kind, page, total)
    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        )


def _main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Хост", callback_data="m:host"),
                InlineKeyboardButton(text="VM", callback_data="m:vm:0"),
                InlineKeyboardButton(text="LXC", callback_data="m:lx:0"),
            ],
            [InlineKeyboardButton(text="Обновить", callback_data="m:refresh")],
        ]
    )


def _guest_actions_keyboard(guest: dict) -> InlineKeyboardMarkup:
    kind = guest["kind"]
    vmid = guest["vmid"]
    status = guest.get("status", "unknown")
    prefix = "q" if kind == "qemu" else "l"
    rows: list[list[InlineKeyboardButton]] = []
    if status == "stopped":
        rows.append([InlineKeyboardButton(text="Запуск", callback_data=f"a:{prefix}:{vmid}:start")])
    elif status == "running":
        rows.append(
            [
                InlineKeyboardButton(text="Пауза", callback_data=f"a:{prefix}:{vmid}:suspend"),
                InlineKeyboardButton(text="Стоп", callback_data=f"a:{prefix}:{vmid}:stop"),
            ]
        )
        rows.append(
            [
                InlineKeyboardButton(
                    text="Перезагрузить",
                    callback_data=f"a:{prefix}:{vmid}:reboot",
                ),
            ]
        )
        rows.append(
            [
                InlineKeyboardButton(
                    text="Выключить",
                    callback_data=f"a:{prefix}:{vmid}:shutdown",
                ),
            ]
        )
    elif status == "paused":
        rows.append(
            [
                InlineKeyboardButton(
                    text="Продолжить",
                    callback_data=f"a:{prefix}:{vmid}:resume",
                ),
                InlineKeyboardButton(text="Стоп", callback_data=f"a:{prefix}:{vmid}:stop"),
            ]
        )
    rows.append(
        [
            InlineKeyboardButton(
                text=status_button_label(status),
                callback_data=f"st:{prefix}:{vmid}",
            )
        ]
    )
    back_kind = "m:vm:0" if kind == "qemu" else "m:lx:0"
    rows.append([InlineKeyboardButton(text="« Список", callback_data=back_kind)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _parse_page(data: str, default: int = 0) -> int:
    try:
        return int(data.rsplit(":", 1)[-1])
    except ValueError:
        return default


def _parse_guest_ref(data: str) -> tuple[str | None, int | None]:
    parts = data.split(":")
    if len(parts) != 3:
        return None, None
    if parts[0] not in ("g", "st"):
        return None, None
    kind = "qemu" if parts[1] == "q" else "lxc" if parts[1] == "l" else None
    try:
        vmid = int(parts[2])
    except ValueError:
        return None, None
    return kind, vmid


def _parse_action(data: str) -> tuple[str | None, int | None, str | None]:
    parts = data.split(":")
    if len(parts) != 4:
        return None, None, None
    kind = "qemu" if parts[1] == "q" else "lxc" if parts[1] == "l" else None
    try:
        vmid = int(parts[2])
    except ValueError:
        return None, None, None
    return kind, vmid, parts[3]


def _parse_confirm(data: str) -> tuple[str | None, int | None, str | None]:
    parts = data.split(":")
    if len(parts) != 4:
        return None, None, None
    kind = "qemu" if parts[1] == "q" else "lxc" if parts[1] == "l" else None
    try:
        vmid = int(parts[2])
    except ValueError:
        return None, None, None
    return kind, vmid, parts[3]


async def _reply_error(callback: CallbackQuery, text: str) -> None:
    await callback.answer("Ошибка", show_alert=True)
    if callback.message:
        await callback.message.answer(text[:300])


def _actor_from_callback(callback: CallbackQuery) -> dict | None:
    user = callback.from_user
    if user is None:
        return None
    return {
        "id": user.id,
        "full_name": user.full_name,
        "username": user.username,
    }
