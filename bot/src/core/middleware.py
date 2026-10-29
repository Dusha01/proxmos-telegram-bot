from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from src.api.api_client import ApiClient


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
            return None
        data["user_id"] = user_id
        data["chat_id"] = chat_id
        data["api"] = self._api
        return await handler(event, data)


def _extract_ids(event: TelegramObject) -> tuple[int | None, int | None]:
    if isinstance(event, Message) and event.from_user and event.chat:
        return event.from_user.id, event.chat.id
    if isinstance(event, CallbackQuery) and event.from_user and event.message:
        return event.from_user.id, event.message.chat.id
    return None, None
