from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

from src.api.api_client import ApiClient

logger = logging.getLogger(__name__)

ACCESS_DENIED_TEXT = "Нет доступа."

class AccessMiddleware(BaseMiddleware):
    def __init__(self, api_client: ApiClient) -> None:
        self._api = api_client

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id, chat_id = _extract_ids(event)
        if user_id is None or chat_id is None:
            return None
        allowed = await self._api.check_access(user_id, chat_id)
        if not allowed:
            await _reply_access_denied(event, user_id, chat_id)
            return None
        data["user_id"] = user_id
        data["chat_id"] = chat_id
        data["api"] = self._api
        return await handler(event, data)


def _extract_ids(event: TelegramObject) -> tuple[int | None, int | None]:
    if isinstance(event, Update):
        if event.message:
            return _extract_ids(event.message)
        if event.callback_query:
            return _extract_ids(event.callback_query)
        if event.edited_message:
            return _extract_ids(event.edited_message)
        return None, None
    if isinstance(event, Message) and event.from_user and event.chat:
        return event.from_user.id, event.chat.id
    if isinstance(event, CallbackQuery) and event.from_user and event.message:
        return event.from_user.id, event.message.chat.id
    return None, None


async def _reply_access_denied(
    event: TelegramObject,
    user_id: int,
    chat_id: int,
) -> None:
    logger.warning(
        "access denied for user_id=%s chat_id=%s (check ADMIN_USER_ID / ADMIN_CHAT_ID in backend)",
        user_id,
        chat_id,
    )
    text = ACCESS_DENIED_TEXT
    if isinstance(event, Update):
        if event.message:
            await event.message.answer(text)
        elif event.callback_query:
            await event.callback_query.answer(ACCESS_DENIED_TEXT, show_alert=True)
        elif event.edited_message:
            await event.edited_message.answer(text)
        return
    if isinstance(event, Message):
        await event.answer(text)
    elif isinstance(event, CallbackQuery):
        await event.answer(ACCESS_DENIED_TEXT, show_alert=True)
