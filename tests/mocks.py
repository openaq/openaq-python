from typing import Any, Mapping

import httpx


class MockTransport:
    def __init__(self, response: httpx.Response = None):
        self.response = response

    def send_request(
        self,
        method: str,
        url: str,
        params: Mapping[str, str],
        headers: Mapping[str, Any],
    ):
        return self.response

    def close(self):
        ...
