from __future__ import annotations

from typing import Any, Mapping

import httpx

from ..shared.transport import BaseTransport, check_response


class AsyncTransport(BaseTransport):
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def send_request(
        self,
        method: str,
        url: str,
        params: Mapping[str, str] | None,
        headers: Mapping[str, Any],
    ):
        request = httpx.Request(
            method=method,
            url=url,
            params=params,
            headers=headers,
        )
        res = await self.client.send(request)
        return check_response(res)

    async def close(self):
        await self.client.aclose()
