import os
import platform
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import pytest

from openaq import __version__
from openaq._sync.client import OpenAQ
from openaq.shared.exceptions import ApiKeyMissingError

from ..mocks import MockTransport


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

    def test_transport_property(self, setup):
        assert self.client.transport == MockTransport
        with pytest.raises(AttributeError):
            self.client.transport = MockTransport

    def test_default_client_params(self, setup):
        assert self.client._base_url == "https://api.openaq.org/v3/"

    def test_default_headers(self, setup):
        assert (
            self.client.headers["User-Agent"]
            == f"openaq-python-{__version__}-{platform.python_version()}"
        )
        assert self.client.headers["Accept"] == "application/json"

    def test_custom_headers(self, setup):
        self.client = OpenAQ(
            api_key="abc123-def456-ghi789",
            base_url="https://mycustom.openaq.org",
            _transport=MockTransport(),
        )
        assert self.client.headers["X-API-Key"] == "abc123-def456-ghi789"

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
        if int(platform.python_version_tuple()[1]) >= 11:
            client = OpenAQ(_transport=MockTransport)
            assert client.api_key == "test_api_key"
        else:
            with pytest.raises(ApiKeyMissingError):
                client = OpenAQ(_transport=MockTransport)

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

    @mock.patch('openaq.shared.client.datetime')
    @mock.patch('time.sleep')
    @mock.patch('openaq._sync.client.logger')
    def test_wait_for_rate_limit_reset_waits_when_positive(
        self, mock_logger, mock_sleep, mock_datetime, setup
    ):
        """Test that sleep is called with correct duration when wait_seconds > 0."""
        now = datetime(2026, 2, 12, 0, 0, 0)
        mock_datetime.now.return_value = now

        # Set reset time to 5 seconds in the future
        self.client._rate_limit_reset_datetime = now + timedelta(seconds=5)

        self.client._wait_for_rate_limit_reset()

        mock_sleep.assert_called_once_with(5)
        mock_logger.info.assert_called_once_with(
            "Rate limit hit. Waiting 5 seconds for reset."
        )

    @mock.patch('openaq.shared.client.datetime')
    @mock.patch('time.sleep')
    @mock.patch('openaq._sync.client.logger')
    def test_wait_for_rate_limit_reset_does_not_wait_when_zero(
        self, mock_logger, mock_sleep, mock_datetime, setup
    ):
        """Test that sleep is not called when wait_seconds is 0."""
        now = datetime(2026, 2, 12, 0, 0, 0)
        mock_datetime.now.return_value = now

        # Set reset time to now (0 seconds wait)
        self.client._rate_limit_reset_datetime = now

        self.client._wait_for_rate_limit_reset()

        mock_sleep.assert_not_called()
        mock_logger.info.assert_not_called()

    @mock.patch('openaq.shared.client.datetime')
    @mock.patch('time.sleep')
    @mock.patch('openaq._sync.client.logger')
    def test_wait_for_rate_limit_reset_does_not_wait_when_negative(
        self, mock_logger, mock_sleep, mock_datetime, setup
    ):
        """Test that sleep is not called when wait_seconds is negative."""
        now = datetime(2026, 2, 12, 0, 0, 0)
        mock_datetime.now.return_value = now

        # Set reset time to 5 seconds in the past
        self.client._rate_limit_reset_datetime = now - timedelta(seconds=5)

        self.client._wait_for_rate_limit_reset()

        mock_sleep.assert_not_called()
        mock_logger.info.assert_not_called()

    def test_close_closes_transport(self, setup):
        """Test that close() calls transport.close()."""
        self.client.transport.close = mock.Mock()

        self.client.close()

        self.client.transport.close.assert_called_once()

    def test_context_manager_enter_returns_client(self, setup):
        """Test that __enter__ returns the client instance."""
        with self.client as ctx_client:
            assert ctx_client is self.client

    def test_context_manager_exit_closes_transport(self, setup):
        """Test that __exit__ calls close() which closes transport."""
        self.client.transport.close = mock.Mock()

        with self.client:
            pass

        self.client.transport.close.assert_called_once()

    def test_context_manager_exit_closes_even_with_exception(self, setup):
        """Test that transport is closed even when exception occurs in context."""
        self.client.transport.close = mock.Mock()

        with pytest.raises(ValueError):
            with self.client:
                raise ValueError("Test exception")

        self.client.transport.close.assert_called_once()
