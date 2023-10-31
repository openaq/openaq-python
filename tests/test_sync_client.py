import platform

import pytest

from openaq._sync.client import OpenAQ

from .mocks import MockTransport


class TestClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = OpenAQ(api_key="abc123-def456-ghi789", _transport=MockTransport)

    def test_default_client_params(self):
        assert self.client._base_url == "https://api.openaq.org/v3/"

    def test_default_headers(self):
        assert (
            self.client._headers["User-Agent"]
            == f"openaq-python-{platform.python_version()}"
        )
        assert self.client._headers["Accept"] == "application/json"

    def test_custom_headers(self):
        self.client = OpenAQ(
            api_key="abc123-def456-ghi789",
            base_url="https://mycustom.openaq.org",
            user_agent="my-custom-useragent",
            _transport=MockTransport(),
        )
        assert self.client._headers["X-API-Key"] == "abc123-def456-ghi789"
        assert self.client._headers["User-Agent"] == "my-custom-useragent"

    def test_client_params(self):
        self.client = OpenAQ(
            api_key="abc123-def456-ghi789",
            base_url="https://mycustom.openaq.org",
            _transport=MockTransport(),
        )
        assert self.client._base_url == "https://mycustom.openaq.org"
