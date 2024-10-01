import os
from typing import Any, Mapping
from unittest import mock

import httpx
import pytest


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

    def close(self): ...


@pytest.fixture(scope='class')
def mock_openaq_api_key_env_vars(scope='class'):
    with mock.patch.dict(
        os.environ, {"OPENAQ_API_KEY": "openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"}
    ):
        yield
