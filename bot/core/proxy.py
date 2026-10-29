from __future__ import annotations

import logging
from typing import Optional

from aiogram.client.session.aiohttp import AiohttpSession

logger = logging.getLogger(__name__)

_EMPTY_PROXY_VALUES = frozenset({"none", "null", "-", "off", "false"})


def normalize_proxy_url(proxy_url: Optional[str]) -> Optional[str]:
    raw = (proxy_url or "").strip()
    if not raw:
        return None
    if raw.lower() in _EMPTY_PROXY_VALUES:
        return None
    return raw


def create_telegram_aiohttp_session(proxy_url: Optional[str]) -> AiohttpSession:
    normalized = normalize_proxy_url(proxy_url)
    if normalized is None:
        logger.info("Telegram API: прямое подключение (без прокси)")
        return AiohttpSession()

    low = normalized.lower()
    if low.startswith(("socks5://", "socks5h://", "socks4://")):
        logger.info("Telegram API: SOCKS-прокси %s", _mask_proxy_url(normalized))
    else:
        logger.info("Telegram API: HTTP(S)-прокси %s", _mask_proxy_url(normalized))

    return AiohttpSession(proxy=normalized)


def _mask_proxy_url(url: str) -> str:
    if "@" not in url:
        return url
    scheme, _, rest = url.partition("://")
    creds, _, host = rest.rpartition("@")
    if ":" in creds:
        user = creds.split(":", 1)[0]
        return f"{scheme}://{user}:***@{host}"
    return f"{scheme}://***@{host}"
