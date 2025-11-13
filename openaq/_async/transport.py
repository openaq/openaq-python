from typing import Mapping

import httpx

from ..shared.transport import check_response


class AsyncTransport:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(timeout=15.0)

    async def send_request(
        self,
        method: str,
        url: str,
        params: httpx.QueryParams | Mapping[str, str | int | float | bool] | None,
        headers: httpx.Headers | Mapping[str, str],
    ) -> httpx.Response:
        request = httpx.Request(
            method=method,
            url=url,
            params=params,
            headers=headers,
        )
        res = await self.client.send(request)
        return check_response(res)

    async def close(self) -> None:
        await self.client.aclose()
