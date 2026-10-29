from __future__ import annotations

from typing import Any

import httpx


class ApiClientError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    def __init__(self, base_url: str, bot_token: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._bot_token = bot_token
        self._timeout = timeout

    def _headers(self, user_id: int, chat_id: int) -> dict[str, str]:
        return {
            "X-Bot-Token": self._bot_token,
            "X-Telegram-User-Id": str(user_id),
            "X-Telegram-Chat-Id": str(chat_id),
        }

    async def check_access(self, user_id: int, chat_id: int) -> bool:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                f"{self._base_url}/access",
                headers=self._headers(user_id, chat_id),
            )
        return response.status_code == 204

    async def _request(
        self,
        method: str,
        path: str,
        user_id: int,
        chat_id: int,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.request(
                method,
                f"{self._base_url}{path}",
                headers=self._headers(user_id, chat_id),
                params=params,
            )
        if response.status_code >= 400:
            detail = response.text[:300]
            raise ApiClientError(
                f"API {response.status_code}: {detail}",
                status_code=response.status_code,
            )
        if response.status_code == 204:
            return None
        if not response.content:
            return None
        return response.json()

    async def get_summary(self, user_id: int, chat_id: int) -> dict[str, Any]:
        return await self._request("GET", "/summary", user_id, chat_id)

    async def get_node(self, user_id: int, chat_id: int) -> dict[str, Any]:
        return await self._request("GET", "/node", user_id, chat_id)

    async def list_guests(
        self,
        user_id: int,
        chat_id: int,
        kind: str,
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/guests",
            user_id,
            chat_id,
            params={"kind": kind},
        )

    async def get_guest(
        self,
        user_id: int,
        chat_id: int,
        kind: str,
        vmid: int,
    ) -> dict[str, Any]:
        return await self._request("GET", f"/guests/{kind}/{vmid}", user_id, chat_id)

    async def guest_action(
        self,
        user_id: int,
        chat_id: int,
        kind: str,
        vmid: int,
        action: str,
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/guests/{kind}/{vmid}/{action}",
            user_id,
            chat_id,
        )

    async def node_shutdown(self, user_id: int, chat_id: int) -> dict[str, Any]:
        return await self._request("POST", "/node/shutdown", user_id, chat_id)
