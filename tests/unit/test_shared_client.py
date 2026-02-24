import os
import platform
from http import HTTPStatus
from pathlib import Path
from unittest import mock
from unittest.mock import mock_open, patch

import httpx
import pytest

from openaq import __version__
from openaq.shared.client import BaseClient, _get_openaq_config, _has_toml
from openaq.shared.exceptions import ApiKeyMissingError
from tests.unit.mocks import MockTransport


def test_tomllib_conditional_import():
    if int(platform.python_version_tuple()[1]) >= 11:
        assert _has_toml == True
    else:
        assert _has_toml == False


def test__get_openaq_config_file_exists():
    mock_toml_content = b"""
        api-key = 'openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p'
    """
    expected_config = {"api_key": "openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"}

    with patch.object(Path, 'is_file', return_value=True):
        with patch(
            'builtins.open', mock_open(read_data=mock_toml_content)
        ) as mock_file:
            result = None
            if int(platform.python_version_tuple()[1]) >= 11:
                result = _get_openaq_config()
                assert result == expected_config
                mock_file.assert_any_call(Path(Path.home() / ".openaq.toml"), 'rb')
            else:
                assert result == None


DEFAULT_USER_AGENT = f"openaq-python-{__version__}-{platform.python_version()}"


class SharedClient(BaseClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_agent = DEFAULT_USER_AGENT
        self.resolve_headers()

    def close():
        pass

    def _do():
        pass

    def _get():
        pass

    def _set_rate_limit(self, headers):
        pass


@pytest.fixture
def mock_config_file():
    mock_toml_content = b"""api-key='test_api_key'"""
    with mock.patch.object(Path, 'is_file', return_value=True):
        with mock.patch(
            'builtins.open', mock.mock_open(read_data=mock_toml_content)
        ) as mock_file:
            yield mock_file


class TestSharedClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.instance = SharedClient(
            MockTransport,
            api_key='abc123-def456-ghi789',
            headers={'this': 'that'},
            auto_wait=False,
        )

    @pytest.mark.usefixtures("mock_config_file")
    def test__get_api_key(self):
        if int(platform.python_version_tuple()[1]) >= 11:
            assert self.instance._get_api_key() == 'test_api_key'
        else:
            assert self.instance._get_api_key() == None

    def test_no_api_key_throws(self):
        with pytest.raises(ApiKeyMissingError):
            instance = SharedClient(MockTransport)

    @pytest.fixture()
    def mock_openaq_api_key_env_vars(self):
        with mock.patch.dict(
            os.environ, {"OPENAQ_API_KEY": "openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"}
        ):
            yield

    def test_api_env_var(self, mock_openaq_api_key_env_vars):
        """
        tests that api_key is set from environment variable
        """
        assert self.instance._get_api_key() == "openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"

    def test_api_key_arg_override_env_var(self, mock_openaq_api_key_env_vars):
        """
        tests that api_key argument overrides api key value set in system environment variable
        """
        assert self.instance.api_key == "abc123-def456-ghi789"

    def test_api_key_arg_override_env_var(self, mock_config_file):
        """
        tests that api_key argument overrides api key value set in openaq config
        """
        assert self.instance.api_key == "abc123-def456-ghi789"

    def test_api_key_arg_override_env_vars_config(
        self, mock_openaq_api_key_env_vars, mock_config_file
    ):
        """
        tests that api_key argument overrides api key value set in config file and system environment variable
        """
        assert self.instance.api_key == "abc123-def456-ghi789"

    def test_api_key_property(self):
        assert self.instance.api_key == 'abc123-def456-ghi789'
        with pytest.raises(AttributeError):
            self.instance.api_key = 'foobarbaz'

    def test_base_url_property(self):
        assert self.instance.base_url == "https://api.openaq.org/v3/"
        with pytest.raises(AttributeError):
            self.instance.base_url = "https://example.com"

    def test_transport_property(self):
        assert self.instance.transport == MockTransport
        with pytest.raises(AttributeError):
            self.instance.transport = 'foobarbaz'

    def test_headers_property(self):
        assert self.instance.headers == {
            'this': 'that',
            'Accept': 'application/json',
            'X-API-Key': 'abc123-def456-ghi789',
            'User-Agent': DEFAULT_USER_AGENT,
        }
        with pytest.raises(AttributeError):
            self.instance.headers = {'openaq': 'api'}

    def test_build_request_headers(self):
        request_headers = self.instance.build_request_headers(
            {'Accept-Language': 'en-US,en;q=0.5'}
        )
        assert request_headers == {
            'this': 'that',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-API-Key': 'abc123-def456-ghi789',
            'User-Agent': DEFAULT_USER_AGENT,
        }

    def test_build_request_headers_none(self):
        request_headers = self.instance.build_request_headers()
        assert request_headers == {
            'this': 'that',
            'Accept': 'application/json',
            'X-API-Key': 'abc123-def456-ghi789',
            'User-Agent': DEFAULT_USER_AGENT,
        }

    def test_auto_wait_default_is_true(self):
        """Test that auto_wait defaults to True."""
        instance = SharedClient(
            MockTransport, api_key='openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p'
        )
        assert instance._auto_wait == True
