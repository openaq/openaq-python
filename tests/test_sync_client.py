import os
import platform

import pytest

from openaq import __version__
from openaq._sync.client import OpenAQ

from .mocks import MockTransport


class TestClient:
    @pytest.fixture()
    def setup(self):
        self.client = OpenAQ(api_key="abc123-def456-ghi789", _transport=MockTransport)

    def test_default_client_params(self, setup):
        assert self.client._BaseClient__base_url == "https://api.openaq.org/v3/"

    def test_default_headers(self, setup):
        assert (
            self.client._headers["User-Agent"]
            == f"openaq-python-{__version__}-{platform.python_version()}"
        )
        assert self.client.headers["Accept"] == "application/json"

    def test_custom_headers(self):
        self.client = OpenAQ(
            api_key="abc123-def456-ghi789",
            base_url="https://mycustom.openaq.org",
            user_agent="my-custom-useragent",
            _transport=MockTransport(),
        )
        assert self.client.headers["X-API-Key"] == "abc123-def456-ghi789"
        assert self.client.headers["User-Agent"] == "my-custom-useragent"

    def test_client_params(self):
        self.client = OpenAQ(
            api_key="abc123-def456-ghi789",
            base_url="https://mycustom.openaq.org",
            _transport=MockTransport(),
        )
        assert self.client.base_url == "https://mycustom.openaq.org"

    def test_client_api_key_env_vars(self):
        os.environ["OPENAQ-API-KEY"] = "1"
        self.client = OpenAQ(
            _transport=MockTransport(),
        )
        assert self.client.api_key == "1"
