import os
from pathlib import Path
import platform
from unittest import mock

import pytest

from openaq import __version__
from openaq._sync.client import OpenAQ

from .mocks import MockTransport


@pytest.fixture
def mock_config_file():
    mock_toml_content = b"""api-key='test_api_key'"""
    with mock.patch.object(Path, 'is_file', return_value=True):
        with mock.patch(
            'builtins.open', mock.mock_open(read_data=mock_toml_content)
        ) as mock_file:
            yield mock_file


class TestClient:
    @pytest.fixture()
    def setup(self):
        self.client = OpenAQ(api_key="abc123-def456-ghi789", _transport=MockTransport)

    @pytest.fixture()
    def mock_openaq_api_key_env_vars(self):
        with mock.patch.dict(
            os.environ, {"OPENAQ_API_KEY": "openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"}
        ):
            yield
            
    def test_default_client_params(self, setup):
        assert self.client._BaseClient__base_url == "https://api.openaq.org/v3/"

    def test_default_headers(self, setup):
        assert (
            self.client._headers["User-Agent"]
            == f"openaq-python-{__version__}-{platform.python_version()}"
        )
        assert self.client.headers["Accept"] == "application/json"

    def test_custom_headers(self, setup):
        self.client = OpenAQ(
            api_key="abc123-def456-ghi789",
            base_url="https://mycustom.openaq.org",
            user_agent="my-custom-useragent",
            _transport=MockTransport(),
        )
        assert self.client.headers["X-API-Key"] == "abc123-def456-ghi789"
        assert self.client.headers["User-Agent"] == "my-custom-useragent"

    def test_client_params(self, setup):
        self.client = OpenAQ(
            api_key="abc123-def456-ghi789",
            base_url="https://mycustom.openaq.org",
            _transport=MockTransport(),
        )
        assert self.client._base_url == "https://mycustom.openaq.org"

    def test_api_env_var(self, mock_openaq_api_key_env_vars):
        """
        tests that api_key is set from environment variable
        """
        client = OpenAQ(_transport=MockTransport)
        assert client.api_key == "openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"

    @pytest.mark.usefixtures("mock_config_file")
    def test_api_key_from_config(self):
        client = OpenAQ(_transport=MockTransport)
        if int(platform.python_version_tuple()[1]) >= 11:
            assert client.api_key == "test_api_key"
        else:
            assert client.api_key == None

    def test_api_key_arg_override_env_var(self, setup, mock_openaq_api_key_env_vars):
        """
        tests that api_key argument overrides api key value set in system environment variable
        """
        assert self.client.api_key == "abc123-def456-ghi789"

    def test_api_key_arg_override_env_var(self, setup, mock_config_file):
        """
        tests that api_key argument overrides api key value set in openaq config
        """
        assert self.client.api_key == "abc123-def456-ghi789"

    def test_api_key_arg_override_env_vars_config(
        self, setup, mock_openaq_api_key_env_vars, mock_config_file
    ):
        """
        tests that api_key argument overrides api key value set in config file and system environment variable
        """
        assert self.client.api_key == "abc123-def456-ghi789"

    def test_client_api_key_env_vars(self):
        os.environ["OPENAQ-API-KEY"] = "1"
        self.client = OpenAQ(
            _transport=MockTransport(),
        )
        assert self.client.api_key == "1"
