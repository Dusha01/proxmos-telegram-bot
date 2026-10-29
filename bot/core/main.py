from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.proxy import create_telegram_aiohttp_session
from core.settings import get_settings
from src.api.api_client import ApiClient
from src.core.middleware import AccessMiddleware
from src.handlers.router import router


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    session = create_telegram_aiohttp_session(settings.telegram_proxy_url or None)
    bot = Bot(
        token=settings.telegram_bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    api_client = ApiClient(settings.api_base_url, settings.bot_api_token)
    dp = Dispatcher()
    dp.update.middleware(AccessMiddleware(api_client))
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
