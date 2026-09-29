"""Fixtures for benchmark tests."""

import json
from typing import Any

import pytest

HEADERS = {
    "x-ratelimit-limit": "60",
    "x-ratelimit-remaining": "59",
    "x-ratelimit-used": "1",
    "x-ratelimit-reset": "30",
}


class FakeResponse:
    """Stand-in for transport.Response exposing only what read_response uses."""

    def __init__(self, body: dict[str, Any] | bytes) -> None:
        self._body = body
        self.headers = HEADERS

    def json(self) -> Any:
        if isinstance(self._body, bytes):
            return json.loads(self._body)
        return self._body


@pytest.fixture
def make_response(load_response):
    """Builds a FakeResponse from a captured fixture file.

    Skips the test if the fixture file has not been captured yet.
    """

    def _make(name: str, *, n: int | None = None, raw: bool = False) -> FakeResponse:
        try:
            body = load_response(name)
        except FileNotFoundError:
            pytest.skip(f"tests/fixtures/responses/{name}.json not captured yet")
        if n is not None:
            body = {
                "meta": {**body["meta"], "limit": n, "found": n},
                "results": body["results"][:n],
            }
        return FakeResponse(json.dumps(body).encode() if raw else body)

    return _make
