import os
import platform
from datetime import datetime
from pathlib import Path
from unittest import mock

import httpx
import pytest

from openaq import __version__
from openaq._async.client import AsyncOpenAQ
from openaq.shared.exceptions import ApiKeyMissingError
from openaq.shared.transport import DEFAULT_LIMITS, DEFAULT_TIMEOUT

from ..mocks import AsyncMockTransport

ASYNC_USER_AGENT = f"openaq-python-async-{__version__}-{platform.python_version()}"


@pytest.fixture
def mock_config_file():
    mock_toml_content = b"""api-key='test_api_key'"""
    with mock.patch.object(Path, 'is_file', return_value=True):
        with mock.patch(
            'builtins.open', mock.mock_open(read_data=mock_toml_content)
        ) as mock_file:
            yield mock_file


class TestAsyncClient:

    @pytest.fixture()
    def setup(self):
        self.client = AsyncOpenAQ(
            api_key="abc123-def456-ghi789", transport=AsyncMockTransport
        )

    @pytest.fixture()
    def mock_openaq_api_key_env_vars(self):
        with mock.patch.dict(
            os.environ, {"OPENAQ_API_KEY": "openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"}
        ):
            yield

    def test_transport_property(self, setup):
        assert self.client.transport == AsyncMockTransport
        with pytest.raises(AttributeError):
            self.client.transport = AsyncMockTransport

    def test_default_client_params(self, setup):
        assert self.client._base_url == "https://api.openaq.org/v3/"

    def test_default_headers(self, setup):
        assert self.client.headers["User-Agent"] == ASYNC_USER_AGENT
        assert self.client.headers["Accept"] == "application/json"

    def test_custom_headers(self, setup):
        self.client = AsyncOpenAQ(
            api_key="abc123-def456-ghi789",
            base_url="https://mycustom.openaq.org",
            transport=AsyncMockTransport(),
        )
        assert self.client.headers["X-API-Key"] == "abc123-def456-ghi789"

    def test_client_params(self, setup):
        self.client = AsyncOpenAQ(
            api_key="abc123-def456-ghi789",
            base_url="https://mycustom.openaq.org",
            transport=AsyncMockTransport(),
        )
        assert self.client._base_url == "https://mycustom.openaq.org"

    def test_api_env_var(self, mock_openaq_api_key_env_vars):
        """
        tests that api_key is set from environment variable
        """
        client = AsyncOpenAQ(transport=AsyncMockTransport)
        assert client.api_key == "openaq-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"

    @pytest.mark.usefixtures("mock_config_file")
    def test_api_key_from_config(self):
        if int(platform.python_version_tuple()[1]) >= 11:
            client = AsyncOpenAQ(transport=AsyncMockTransport)
            assert client.api_key == "test_api_key"
        else:
            with pytest.raises(ApiKeyMissingError):
                client = AsyncOpenAQ(transport=AsyncMockTransport)

    def test_api_key_arg_override_env_var(self, setup, mock_openaq_api_key_env_vars):
        """
        tests that api_key argument overrides api key value set in system environment variable
        """
        assert self.client.api_key == "abc123-def456-ghi789"

    def test_api_key_arg_override_config(self, setup, mock_config_file):
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

    @pytest.mark.asyncio
    async def test_close_closes_transport(self, setup):
        """Test that close() calls transport.close()."""
        self.client.transport.close = mock.AsyncMock()

        await self.client.close()

        self.client.transport.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_enter_returns_client(self, setup):
        """Test that __aenter__ returns the client instance."""
        async with self.client as ctx_client:
            assert ctx_client is self.client

    @pytest.mark.asyncio
    async def test_context_manager_exit_closes_transport(self, setup):
        """Test that __aexit__ calls close() which closes transport."""
        self.client.transport.close = mock.AsyncMock()

        async with self.client:
            pass

        self.client.transport.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_exit_closes_even_with_exception(self, setup):
        """Test that transport is closed even when exception occurs in context."""
        self.client.transport.close = mock.AsyncMock()

        with pytest.raises(ValueError):
            async with self.client:
                raise ValueError("Test exception")

        self.client.transport.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_acquire_token_grants_when_capacity_available(self, setup):
        """Test that token is granted immediately when capacity is available."""
        self.client._rate_limit_remaining = 60.0
        self.client._in_flight_requests = 0
        initial_in_flight = self.client._in_flight_requests

        await self.client._acquire_token()

        assert self.client._in_flight_requests == initial_in_flight + 1

    @pytest.mark.asyncio
    async def test_acquire_token_raises_when_exhausted_and_auto_wait_false(self, setup):
        """Test that RateLimitError is raised when exhausted and auto_wait is False."""
        from openaq.shared.exceptions import RateLimitError

        self.client._auto_wait = False
        self.client._rate_limit_remaining = 0.0
        self.client._in_flight_requests = 0

        with pytest.raises(RateLimitError):
            await self.client._acquire_token()

    @pytest.mark.asyncio
    async def test_acquire_token_resets_capacity_on_new_window(self, setup):
        """Test that capacity resets when minute window rolls over."""
        self.client._rate_limit_remaining = 0.0
        self.client._in_flight_requests = 0
        self.client._current_window_id = "202602240000"

        with mock.patch('openaq._async.client.datetime') as mock_datetime:
            now = datetime(2026, 2, 24, 0, 1, 0)
            mock_datetime.now.return_value = now

            await self.client._acquire_token()

        assert self.client._in_flight_requests == 1

    @pytest.mark.asyncio
    async def test_acquire_token_accounts_for_in_flight_on_window_reset(self, setup):
        """Test that in-flight requests are subtracted from capacity on window reset."""
        self.client._rate_limit_remaining = 0.0
        self.client._in_flight_requests = 5
        self.client._current_window_id = "202602240000"

        with mock.patch('openaq._async.client.datetime') as mock_datetime:
            now = datetime(2026, 2, 24, 0, 1, 0)
            mock_datetime.now.return_value = now

            await self.client._acquire_token()

        assert self.client._rate_limit_remaining == self.client._rate_limit_capacity - 5

    @pytest.mark.asyncio
    async def test_acquire_token_decrements_in_flight_on_completion(self, setup):
        """Test that in-flight counter is decremented after request completes."""
        mock_response = mock.MagicMock()
        mock_response.headers = {}
        self.client.transport.send_request = mock.AsyncMock(return_value=mock_response)

        await self.client._do("get", "/test")

        assert self.client._in_flight_requests == 0

    @pytest.mark.asyncio
    async def test_acquire_token_decrements_in_flight_on_exception(self, setup):
        """Test that in-flight counter is decremented even when request raises."""
        self.client.transport.send_request = mock.AsyncMock(
            side_effect=Exception("network error")
        )

        with pytest.raises(Exception, match="network error"):
            await self.client._do("get", "/test")

        assert self.client._in_flight_requests == 0

    @pytest.mark.asyncio
    async def test_set_rate_limit_updates_remaining_from_headers(self, setup):
        """Test that remaining is updated from x-ratelimit-remaining header."""
        headers = httpx.Headers(
            {"x-ratelimit-remaining": "45", "x-ratelimit-limit": "60"}
        )
        self.client._set_rate_limit(headers)
        assert self.client._rate_limit_remaining == 45.0

    @pytest.mark.asyncio
    async def test_set_rate_limit_updates_capacity_from_headers(self, setup):
        """Test that capacity is updated from x-ratelimit-limit header."""
        headers = httpx.Headers(
            {"x-ratelimit-remaining": "45", "x-ratelimit-limit": "120"}
        )
        self.client._set_rate_limit(headers)
        assert self.client._rate_limit_capacity == 120.0

    @pytest.mark.asyncio
    async def test_set_rate_limit_server_remaining_overrides_local_count(self, setup):
        """Test that server-provided remaining overrides optimistic local tracking."""

        self.client._rate_limit_remaining = 50.0
        headers = httpx.Headers(
            {"x-ratelimit-remaining": "30", "x-ratelimit-limit": "60"}
        )
        self.client._set_rate_limit(headers)
        assert self.client._rate_limit_remaining == 30.0

    @pytest.mark.asyncio
    async def test_rate_limit_synced_event_set_after_first_request(self, setup):
        """Test that rate limit sync event is set after the first request completes."""
        mock_response = mock.MagicMock()
        mock_response.headers = {}
        self.client.transport.send_request = mock.AsyncMock(return_value=mock_response)

        assert not self.client._rate_limit_synced_event.is_set()
        await self.client._do("get", "/test")
        assert self.client._rate_limit_synced_event.is_set()

    @pytest.mark.asyncio
    async def test_rate_limit_synced_event_set_even_on_request_failure(self, setup):
        """Test that sync event is set even when the first request fails."""
        self.client.transport.send_request = mock.AsyncMock(
            side_effect=Exception("network error")
        )

        with pytest.raises(Exception):
            await self.client._do("get", "/test")

        assert self.client._rate_limit_synced_event.is_set()

    @pytest.mark.asyncio
    async def test_default_rate_limit_override(self, setup):
        """Test that default rate limit capacity is set to 60."""
        assert self.client._rate_limit_capacity == 60.0

    @pytest.mark.asyncio
    async def test_custom_rate_limit_override(self):
        """Test that rate_limit_override sets custom capacity."""
        client = AsyncOpenAQ(
            api_key="abc123-def456-ghi789",
            transport=AsyncMockTransport(),
            rate_limit_override=30,
        )
        assert client._rate_limit_capacity == 30.0
        assert client._rate_limit_remaining == 30.0

    @pytest.mark.asyncio
    async def test_blocks_after_custom_limit(self):
        """Test that client raises after exhausting custom rate limit."""
        from openaq.shared.exceptions import RateLimitError

        client = AsyncOpenAQ(
            api_key="abc123-def456-ghi789",
            transport=AsyncMockTransport(),
            auto_wait=False,
            rate_limit_override=5,
        )
        for _ in range(5):
            await client._acquire_token()

        with pytest.raises(RateLimitError):
            await client._acquire_token()

    def test_default_timeout_applied_to_transport(self):
        """Test that default timeout is applied to the transport."""
        client = AsyncOpenAQ(api_key="abc123-def456-ghi789")
        assert client.transport.client.timeout == DEFAULT_TIMEOUT

    def test_custom_timeout_passed_to_transport(self):
        """Test that a custom timeout is passed through to the transport."""
        custom_timeout = httpx.Timeout(10.0, read=15.0)
        client = AsyncOpenAQ(api_key="abc123-def456-ghi789", timeout=custom_timeout)
        assert client.transport.client.timeout == custom_timeout

    def test_default_limits_applied_to_transport(self):
        """Test that default connection limits are applied to the transport."""
        with mock.patch('openaq._async.transport.httpx.AsyncClient') as mock_client:
            AsyncOpenAQ(api_key="abc123-def456-ghi789")
            mock_client.assert_called_once_with(
                timeout=DEFAULT_TIMEOUT, limits=DEFAULT_LIMITS
            )

    def test_custom_limits_passed_to_transport(self):
        """Test that custom connection limits are passed through to the transport."""
        custom_limits = httpx.Limits(max_connections=5, max_keepalive_connections=2)
        with mock.patch('openaq._async.transport.httpx.AsyncClient') as mock_client:
            AsyncOpenAQ(api_key="abc123-def456-ghi789", limits=custom_limits)
            mock_client.assert_called_once_with(
                timeout=DEFAULT_TIMEOUT, limits=custom_limits
            )
