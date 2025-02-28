from __future__ import annotations

from typing import Any, Mapping

import httpx

from openaq.shared.transport import check_response


class Transport:
    def __init__(self):
        self.client = httpx.Client()

    def send_request(
        self,
        method: str,
        url: str,
        params: Mapping[str, str] | None,
        headers: Mapping[str, Any],
    ):
        """Sends an HTTP request using the provided method, URL, parameters, and headers."""
        request = httpx.Request(
            method=method,
            url=url,
            params=params,
            headers=headers,
        )
        res = self.client.send(request)
        return check_response(res)

    def close(self):
        self.client.close()
