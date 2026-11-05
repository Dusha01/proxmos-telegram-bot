from __future__ import annotations

import httpx

from influx.errors import InfluxError


class InfluxClient:
    def __init__(
        self,
        *,
        url: str,
        org: str,
        token: str,
        timeout: float = 15.0,
    ) -> None:
        base = url.rstrip("/")
        self._query_url = f"{base}/api/v2/query"
        self._org = org
        self._token = token
        self._timeout = timeout

    async def query_csv(self, flux: str) -> str:
        headers = {
            "Authorization": f"Token {self._token}",
            "Accept": "application/csv",
            "Content-Type": "application/vnd.flux",
        }
        params = {"org": self._org}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                self._query_url,
                params=params,
                headers=headers,
                content=flux,
            )
        if response.status_code >= 400:
            detail = response.text[:500]
            raise InfluxError(
                f"InfluxDB HTTP {response.status_code}: {detail}",
                status_code=response.status_code,
            )
        body = response.text
        if body.lstrip().startswith("{"):
            raise InfluxError(f"InfluxDB query error: {body[:500]}")
        return body
