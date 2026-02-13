import os
import platform
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from unittest import mock
from unittest.mock import mock_open, patch

import httpx
import pytest
from freezegun import freeze_time

from openaq.shared.client import (
    DEFAULT_USER_AGENT,
    BaseClient,
    _get_openaq_config,
    _has_toml,
)
from openaq.shared.exceptions import ApiKeyMissingError, RateLimitError
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


class SharedClient(BaseClient):
    def close():
        pass

    def _do():
        pass

    def _get():
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
            'User-Agent': DEFAULT_USER_AGENT,
            'X-API-Key': 'abc123-def456-ghi789',
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
            'User-Agent': DEFAULT_USER_AGENT,
            'X-API-Key': 'abc123-def456-ghi789',
        }

    def test_build_request_headers_none(self):
        request_headers = self.instance.build_request_headers()
        assert request_headers == {
            'this': 'that',
            'Accept': 'application/json',
            'User-Agent': DEFAULT_USER_AGENT,
            'X-API-Key': 'abc123-def456-ghi789',
        }

    def test___check_rate_limit(self):
        mock_response = httpx.Response(
            HTTPStatus.OK,
            content="Test content",
            headers={
                'X-RateLimit-Used': '0',
                'X-RateLimit-Reset': '60',
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Limit': '60',
            },
        )
        self.instance._set_rate_limit(mock_response.headers)
        with pytest.raises(RateLimitError):
            self.instance._check_rate_limit()

    @freeze_time("2025-02-27T01:00:00")
    def test__is_rate_limited(self):
        mock_response = httpx.Response(
            HTTPStatus.OK,
            content="Test content",
            headers={
                'X-RateLimit-Used': '0',
                'X-RateLimit-Reset': '60',
                'X-RateLimit-Remaining': '59',
                'X-RateLimit-Limit': '60',
            },
        )
        self.instance._set_rate_limit(mock_response.headers)
        assert self.instance._rate_limit_reset_seconds == 60
        assert self.instance._is_rate_limited() == False
        with freeze_time("2025-02-27T01:00:59"):
            assert self.instance._is_rate_limited() == False
            assert self.instance._rate_limit_reset_seconds == 1

    @freeze_time("2025-02-27T01:00:00")
    def test__is_rate_limited_true(self):
        mock_response = httpx.Response(
            HTTPStatus.OK,
            content="Test content",
            headers={
                'X-RateLimit-Used': '0',
                'X-RateLimit-Reset': '30',
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Limit': '60',
            },
        )
        self.instance._set_rate_limit(mock_response.headers)
        with freeze_time("2025-02-27T01:00:29"):
            assert self.instance._rate_limit_remaining == 0
            assert self.instance._rate_limit_reset_seconds == 1
            assert self.instance._rate_limit_reset_datetime == datetime(
                year=2025, month=2, day=27, hour=1, minute=0, second=30
            )
            assert self.instance._is_rate_limited()

    @freeze_time("2025-02-27T01:00:00")
    def test__is_rate_limited_false(self):
        mock_response = httpx.Response(
            HTTPStatus.OK,
            content="Test content",
            headers={
                'X-RateLimit-Used': '0',
                'X-RateLimit-Reset': '30',
                'X-RateLimit-Remaining': '60',
                'X-RateLimit-Limit': '60',
            },
        )
        self.instance._set_rate_limit(mock_response.headers)
        with freeze_time("2025-02-27T01:00:31"):
            assert self.instance._rate_limit_remaining == 60
            assert self.instance._rate_limit_reset_seconds == -1
            assert self.instance._rate_limit_reset_datetime == datetime(
                year=2025, month=2, day=27, hour=1, minute=0, second=30
            )
            assert self.instance._is_rate_limited() == False

    def test_auto_wait_default_is_true(self):
        """Test that auto_wait defaults to True."""
        instance = SharedClient(
            MockTransport, api_key='openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p'
        )
        assert instance._auto_wait == True

    def test_auto_wait_false_raises_rate_limit_error(self):
        """Test that auto_wait=True doesn't raise RateLimitError when rate limited."""
        instance = SharedClient(
            MockTransport,
            api_key='openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p',
        )
        mock_response = httpx.Response(
            HTTPStatus.OK,
            content="Test content",
            headers={
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Reset': '60',
            },
        )
        instance._set_rate_limit(mock_response.headers)
        self.instance._check_rate_limit()  # Should not raise RateLimitError
