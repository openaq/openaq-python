from typing import TYPE_CHECKING, Mapping

from httpx import AsyncClient, Request, Headers, Response

from ..shared.transport import BaseTransport, check_response


class AsyncTransport(BaseTransport):
    def __init__(self) -> None:
        self.client = AsyncClient(timeout=15.0)

    async def send_request(
        self,
        method: str,
        url: str,
        params: Mapping[str, str] | None,
        headers: Headers | Mapping[str, str],
    ) -> Response:
        request = Request(
            method=method,
            url=url,
            params=params,
            headers=headers,
        )
        res = await self.client.send(request)
        return check_response(res)

    async def close(self) -> None:
        await self.client.aclose()
