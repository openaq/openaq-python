import os
import platform
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

import httpx
from openaq.shared.transport import DEFAULT_LIMITS, DEFAULT_TIMEOUT
import pytest
from freezegun import freeze_time

from openaq import __version__
from openaq._sync.client import OpenAQ
from openaq.shared.exceptions import ApiKeyMissingError, RateLimitError

from ..mocks import MockTransport

SYNC_USER_AGENT = f"openaq-python-sync-{__version__}-{platform.python_version()}"


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
        self.client = OpenAQ(api_key="abc123-def456-ghi789", transport=MockTransport)

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
        assert self.client.headers["User-Agent"] == SYNC_USER_AGENT
        assert self.client.headers["Accept"] == "application/json"

    def test_custom_headers(self, setup):
        self.client = OpenAQ(
            api_key="abc123-def456-ghi789",
            base_url="https://mycustom.openaq.org",
            transport=MockTransport(),
        )
        assert self.client.headers["X-API-Key"] == "abc123-def456-ghi789"

    def test_client_params(self, setup):
        self.client = OpenAQ(
            api_key="abc123-def456-ghi789",
            base_url="https://mycustom.openaq.org",
            transport=MockTransport(),
        )
        assert self.client._base_url == "https://mycustom.openaq.org"

    def test_api_env_var(self, mock_openaq_api_key_env_vars):
        """
        tests that api_key is set from environment variable
        """
        client = OpenAQ(transport=MockTransport)
        assert client.api_key == "openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"

    @pytest.mark.usefixtures("mock_config_file")
    def test_api_key_from_config(self):
        if int(platform.python_version_tuple()[1]) >= 11:
            client = OpenAQ(transport=MockTransport)
            assert client.api_key == "test_api_key"
        else:
            with pytest.raises(ApiKeyMissingError):
                client = OpenAQ(transport=MockTransport)

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

    @mock.patch('openaq._sync.client.datetime')
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

    @mock.patch('openaq._sync.client.datetime')
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

    @mock.patch('openaq._sync.client.datetime')
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

    def test_blocks_after_custom_limit(self):
        """Test that client blocks after exhausting custom rate limit."""
        from openaq.shared.exceptions import RateLimitError

        client = OpenAQ(
            api_key="abc123-def456-ghi789",
            transport=MockTransport(),
            auto_wait=False,
            rate_limit_override=5,
        )
        for _ in range(5):
            client._check_rate_limit()
            client._rate_limit_remaining -= 1

        with pytest.raises(RateLimitError):
            client._check_rate_limit()

    def test_allows_exactly_override_requests(self):
        """Test that client allows exactly rate_limit_override requests before blocking."""
        from openaq.shared.exceptions import RateLimitError

        limit = 10
        client = OpenAQ(
            api_key="abc123-def456-ghi789",
            transport=MockTransport(),
            auto_wait=False,
            rate_limit_override=limit,
        )
        success_count = 0
        for _ in range(limit + 5):
            try:
                client._check_rate_limit()
                client._rate_limit_remaining -= 1
                success_count += 1
            except RateLimitError:
                break

        assert success_count == limit

    def test_raises_when_exhausted_and_auto_wait_false(self, setup):
        """Test that RateLimitError is raised when exhausted and auto_wait is False."""
        from openaq.shared.exceptions import RateLimitError

        self.client._auto_wait = False
        self.client._rate_limit_remaining = 0.0
        self.client._rate_limit_reset_datetime = datetime.now() + timedelta(seconds=30)

        with pytest.raises(RateLimitError):
            self.client._check_rate_limit()

    @freeze_time("2026-02-12T00:00:00")
    def test_error_message_includes_reset_seconds(self, setup):
        """Test that RateLimitError message includes seconds until reset."""
        self.client._auto_wait = False
        self.client._rate_limit_remaining = 0.0
        self.client._rate_limit_reset_datetime = datetime(2026, 2, 12, 0, 0, 30)
        self.client._current_window_id = datetime.now().strftime("%Y%m%d%H%M")

        with pytest.raises(RateLimitError, match="30"):
            self.client._check_rate_limit()

    @mock.patch('time.sleep')
    def test_waits_when_exhausted_and_auto_wait_true(self, mock_sleep, setup):
        """Test that sleep is called when exhausted and auto_wait is True."""
        self.client._auto_wait = True
        self.client._rate_limit_remaining = 0.0
        self.client._rate_limit_reset_datetime = datetime.now() + timedelta(seconds=10)

        self.client._check_rate_limit()

        mock_sleep.assert_called_once()

    @mock.patch('time.sleep')
    def test_resets_capacity_after_wait(self, mock_sleep, setup):
        """Test that remaining is reset to full capacity after waiting."""
        self.client._auto_wait = True
        self.client._rate_limit_remaining = 0.0
        self.client._rate_limit_reset_datetime = datetime.now() + timedelta(seconds=10)

        self.client._check_rate_limit()

        assert self.client._rate_limit_remaining == self.client._rate_limit_capacity

    @mock.patch('openaq._sync.client.datetime')
    def test_resets_capacity_on_new_window(self, mock_datetime, setup):
        """Test that capacity resets automatically when minute window rolls over."""
        now = datetime(2026, 2, 12, 0, 1, 0)
        mock_datetime.now.return_value = now

        self.client._rate_limit_remaining = 0.0
        self.client._current_window_id = "202602120000"

        try:
            self.client._check_rate_limit()
        except Exception as e:
            pytest.fail(f"Unexpected exception raised: {e}")

        assert self.client._rate_limit_remaining == self.client._rate_limit_capacity

    @mock.patch('openaq._sync.client.datetime')
    def test_does_not_reset_capacity_within_same_window(self, mock_datetime, setup):
        """Test that capacity is not reset when still within the same window."""
        now = datetime(2026, 2, 12, 0, 0, 30)
        mock_datetime.now.return_value = now
        self.client._current_window_id = now.strftime("%Y%m%d%H%M")
        self.client._rate_limit_remaining = 5.0

        self.client._check_rate_limit()

        assert self.client._rate_limit_remaining == 5.0

    @mock.patch('openaq._sync.client.datetime')
    def test_updates_window_id_on_rollover(self, mock_datetime, setup):
        """Test that window ID is updated when minute window rolls over."""
        now = datetime(2026, 2, 12, 0, 1, 0)
        mock_datetime.now.return_value = now
        self.client._current_window_id = "202602120000"

        self.client._check_rate_limit()

        assert self.client._current_window_id == "202602120001"

    def test_set_rate_limit_updates_remaining_from_headers(self, setup):
        """Test that remaining is updated from x-ratelimit-remaining header."""
        headers = httpx.Headers(
            {"x-ratelimit-remaining": "45", "x-ratelimit-reset": "60"}
        )
        self.client._set_rate_limit(headers)
        assert self.client._rate_limit_remaining == 45

    def test_set_rate_limit_server_remaining_overrides_local_count(self, setup):
        """Test that server-provided remaining overrides optimistic local tracking."""
        self.client._rate_limit_remaining = 50.0
        headers = httpx.Headers(
            {"x-ratelimit-remaining": "30", "x-ratelimit-reset": "60"}
        )
        self.client._set_rate_limit(headers)
        assert self.client._rate_limit_remaining == 30

    def test_set_rate_limit_updates_reset_datetime_from_headers(self, setup):
        """Test that reset datetime is calculated correctly from x-ratelimit-reset header."""
        headers = httpx.Headers(
            {"x-ratelimit-remaining": "45", "x-ratelimit-reset": "30"}
        )
        before = datetime.now() + timedelta(seconds=29)
        self.client._set_rate_limit(headers)
        after = datetime.now() + timedelta(seconds=32)

        assert before < self.client._rate_limit_reset_datetime < after

    def test_set_rate_limit_missing_headers_does_not_raise(self, setup):
        """Test that entirely missing rate limit headers are handled gracefully."""
        headers = httpx.Headers({})
        try:
            self.client._set_rate_limit(headers)
        except Exception as e:
            pytest.fail(f"Unexpected exception raised: {e}")

    def test_set_rate_limit_remaining_allows_further_requests(self, setup):
        """Test that after server sync, requests are allowed up to the new remaining count."""
        from openaq.shared.exceptions import RateLimitError

        headers = httpx.Headers(
            {"x-ratelimit-remaining": "2", "x-ratelimit-reset": "30"}
        )
        self.client._set_rate_limit(headers)
        self.client._auto_wait = False

        self.client._check_rate_limit()
        self.client._rate_limit_remaining -= 1
        self.client._check_rate_limit()
        self.client._rate_limit_remaining -= 1

        with pytest.raises(RateLimitError):
            self.client._check_rate_limit()

    def test_do_calls_transport_with_correct_args(self, setup):
        """Test that _do constructs the correct URL and passes method to transport."""
        mock_response = mock.MagicMock()
        mock_response.headers = httpx.Headers({})
        self.client.transport.send_request = mock.Mock(return_value=mock_response)

        self.client._do("get", "locations/1")

        call_kwargs = self.client.transport.send_request.call_args
        assert call_kwargs.kwargs["url"] == "https://api.openaq.org/v3/locations/1"
        assert call_kwargs.kwargs["method"] == "get"

    def test_do_passes_params_to_transport(self, setup):
        """Test that _do passes query params through to the transport."""
        mock_response = mock.MagicMock()
        mock_response.headers = httpx.Headers({})
        self.client.transport.send_request = mock.Mock(return_value=mock_response)

        self.client._do("get", "/test", params={"limit": 100, "page": 1})

        call_kwargs = self.client.transport.send_request.call_args
        assert call_kwargs.kwargs["params"] == {"limit": 100, "page": 1}

    def test_do_passes_custom_headers_to_transport(self, setup):
        """Test that _do merges custom headers into the request."""
        mock_response = mock.MagicMock()
        mock_response.headers = httpx.Headers({})
        self.client.transport.send_request = mock.Mock(return_value=mock_response)

        self.client._do("get", "/test", headers={"X-Custom-Header": "value"})

        call_kwargs = self.client.transport.send_request.call_args
        assert "X-Custom-Header" in call_kwargs.kwargs["headers"]

    def test_do_syncs_rate_limit_from_response_headers(self, setup):
        """Test that _do updates rate limit state from response headers."""
        mock_response = mock.MagicMock()
        mock_response.headers = httpx.Headers(
            {
                "x-ratelimit-remaining": "42",
                "x-ratelimit-reset": "30",
            }
        )
        self.client.transport.send_request = mock.Mock(return_value=mock_response)

        self.client._do("get", "/test")

        assert self.client._rate_limit_remaining == 42

    def test_do_raises_before_sending_when_rate_limited(self, setup):
        """Test that _do raises RateLimitError without calling transport when exhausted."""
        from openaq.shared.exceptions import RateLimitError

        self.client._auto_wait = False
        self.client._rate_limit_remaining = 0
        self.client._rate_limit_reset_datetime = datetime.now() + timedelta(seconds=30)
        self.client._current_window_id = datetime.now().strftime("%Y%m%d%H%M")
        self.client.transport.send_request = mock.Mock()

        with pytest.raises(RateLimitError):
            self.client._do("get", "/test")

        self.client.transport.send_request.assert_not_called()

    def test_default_timeout_applied_to_transport(self):
        """Test that default timeout is applied to the transport."""
        client = OpenAQ(api_key="abc123-def456-ghi789")
        assert client.transport.client.timeout == DEFAULT_TIMEOUT

    def test_custom_timeout_passed_to_transport(self):
        """Test that a custom timeout is passed through to the transport."""
        custom_timeout = httpx.Timeout(10.0, read=15.0)
        client = OpenAQ(api_key="abc123-def456-ghi789", timeout=custom_timeout)
        assert client.transport.client.timeout == custom_timeout

    def test_default_limits_applied_to_transport(self):
        """Test that default connection limits are applied to the transport."""
        with mock.patch('openaq._sync.transport.httpx.Client') as mock_client:
            OpenAQ(api_key="abc123-def456-ghi789")
            mock_client.assert_called_once_with(
                timeout=DEFAULT_TIMEOUT, limits=DEFAULT_LIMITS
            )

    def test_custom_limits_passed_to_transport(self):
        """Test that custom connection limits are passed through to the transport."""
        custom_limits = httpx.Limits(max_connections=5, max_keepalive_connections=2)
        with mock.patch('openaq._sync.transport.httpx.Client') as mock_client:
            OpenAQ(api_key="abc123-def456-ghi789", limits=custom_limits)
            mock_client.assert_called_once_with(
                timeout=DEFAULT_TIMEOUT, limits=custom_limits
            )
