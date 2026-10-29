from __future__ import annotations

from typing import Any

import httpx


class ProxmoxError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ProxmoxClient:
    def __init__(
        self,
        *,
        host: str,
        token_id: str,
        token_secret: str,
        node: str = "",
        verify_ssl: bool = False,
        timeout: float = 30.0,
    ) -> None:
        base = host.rstrip("/")
        self._api_base = f"{base}/api2/json"
        self._token_id = token_id
        self._token_secret = token_secret
        self._node_override = node.strip()
        self._verify_ssl = verify_ssl
        self._timeout = timeout
        self._node: str | None = None

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"PVEAPIToken={self._token_id}={self._token_secret}",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self._api_base}{path}"
        async with httpx.AsyncClient(verify=self._verify_ssl, timeout=self._timeout) as client:
            response = await client.request(
                method,
                url,
                headers=self._headers(),
                params=params,
                json=json_body,
            )
        if response.status_code >= 400:
            detail = response.text[:500]
            raise ProxmoxError(
                f"Proxmox HTTP {response.status_code}: {detail}",
                status_code=response.status_code,
            )
        payload = response.json()
        if isinstance(payload, dict) and payload.get("errors"):
            raise ProxmoxError(str(payload["errors"]))
        return payload.get("data") if isinstance(payload, dict) else payload

    async def resolve_node(self) -> str:
        if self._node_override:
            self._node = self._node_override
            return self._node
        if self._node:
            return self._node
        nodes = await self._request("GET", "/nodes")
        if not isinstance(nodes, list) or not nodes:
            raise ProxmoxError("Proxmox: нет доступных нод")
        if len(nodes) > 1:
            raise ProxmoxError("Proxmox: несколько нод, задайте PROXMOX_NODE")
        node_name = nodes[0].get("node")
        if not node_name:
            raise ProxmoxError("Proxmox: не удалось определить имя ноды")
        self._node = str(node_name)
        return self._node

    async def get_node_status(self) -> dict[str, Any]:
        node = await self.resolve_node()
        data = await self._request("GET", f"/nodes/{node}/status")
        if not isinstance(data, dict):
            raise ProxmoxError("Proxmox: некорректный ответ status")
        data["node"] = node
        return data

    async def list_qemu(self) -> list[dict[str, Any]]:
        node = await self.resolve_node()
        data = await self._request("GET", f"/nodes/{node}/qemu")
        return data if isinstance(data, list) else []

    async def list_lxc(self) -> list[dict[str, Any]]:
        node = await self.resolve_node()
        data = await self._request("GET", f"/nodes/{node}/lxc")
        return data if isinstance(data, list) else []

    async def guest_status_action(
        self,
        kind: str,
        vmid: int,
        action: str,
    ) -> None:
        node = await self.resolve_node()
        await self._request(
            "POST",
            f"/nodes/{node}/{kind}/{vmid}/status/{action}",
        )

    async def shutdown_node(self) -> None:
        node = await self.resolve_node()
        await self._request(
            "POST",
            f"/nodes/{node}/status",
            json_body={"command": "shutdown"},
        )
