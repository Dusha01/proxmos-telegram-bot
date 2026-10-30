from __future__ import annotations

from aiogram.types import CallbackQuery, Chat, Message, Update, User

from src.core.middleware import _extract_ids


def test_extract_ids_from_update_message() -> None:
    user = User(id=42, is_bot=False, first_name="A")
    chat = Chat(id=42, type="private")
    message = Message(message_id=1, date=0, chat=chat, from_user=user)
    update = Update(update_id=1, message=message)
    assert _extract_ids(update) == (42, 42)


def test_extract_ids_from_update_callback() -> None:
    user = User(id=7, is_bot=False, first_name="A")
    chat = Chat(id=-100, type="supergroup")
    message = Message(message_id=1, date=0, chat=chat)
    callback = CallbackQuery(id="1", from_user=user, chat_instance="x", message=message)
    update = Update(update_id=2, callback_query=callback)
    assert _extract_ids(update) == (7, -100)
