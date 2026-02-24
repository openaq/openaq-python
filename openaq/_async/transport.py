import logging
from typing import Mapping

import httpx

from ..shared.transport import DEFAULT_LIMITS, DEFAULT_TIMEOUT, check_response

logger = logging.getLogger(__name__)


class AsyncTransport:
    def __init__(
        self,
        timeout: float | httpx.Timeout | None = DEFAULT_TIMEOUT,
        limits: httpx.Limits = DEFAULT_LIMITS,
    ) -> None:
        self.client = httpx.AsyncClient(timeout=timeout, limits=limits)

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
        logger.debug(
            f"Sending request to: {request.url}",
            extra={
                'method': method,
                'url': str(request.url),
                'params': params,
            },
        )
        res = await self.client.send(request)
        logger.debug(f"Received response: {res.status_code} from {request.url}")
        return check_response(res)

    async def close(self) -> None:
        await self.client.aclose()
