from typing import Mapping

import httpx

from openaq.shared.transport import check_response


class Transport:
    def __init__(self) -> None:
        self.client = httpx.Client(timeout=15.0)

    def send_request(
        self,
        method: str,
        url: str,
        params: httpx.QueryParams | Mapping[str, str | int | float | bool] | None,
        headers: httpx.Headers | Mapping[str, str],
    ) -> httpx.Response:
        """Sends an HTTP request using the provided method, URL, parameters, and headers."""
        request = httpx.Request(
            method=method,
            url=url,
            params=params,
            headers=headers,
        )
        res = self.client.send(request)
        return check_response(res)

    def close(self) -> None:
        self.client.close()
