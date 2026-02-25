from __future__ import annotations

import asyncio
import logging
import platform
from datetime import datetime
from types import TracebackType
from typing import Mapping

import httpx

from openaq import __version__
from openaq._async.models.countries import Countries
from openaq._async.models.instruments import Instruments
from openaq._async.models.licenses import Licenses
from openaq._async.models.locations import Locations
from openaq._async.models.manufacturers import Manufacturers
from openaq._async.models.measurements import Measurements
from openaq._async.models.owners import Owners
from openaq._async.models.parameters import Parameters
from openaq._async.models.providers import Providers
from openaq._async.models.sensors import Sensors
from openaq.shared.client import DEFAULT_BASE_URL, BaseClient
from openaq.shared.exceptions import RateLimitError
from openaq.shared.transport import DEFAULT_LIMITS, DEFAULT_TIMEOUT

from .transport import AsyncTransport

logger = logging.getLogger(__name__)


class AsyncOpenAQ(BaseClient[AsyncTransport]):
    """OpenAQ asynchronous client.

    Args:
        api_key: The API key for accessing the service.
        headers: Additional headers to be sent with the request.
        auto_wait: Whether to automatically wait when rate limited. Defaults to
            True.
        base_url: The base URL for the API endpoint.
        transport: The transport instance for making HTTP requests. For internal
            use.
        rate_limit_override: Override the default rate limit capacity of 60
            requests per minute.
            Useful for accounts with a higher rate limit. Defaults to 60.
        timeout: Timeout configuration for HTTP requests. Defaults to 5 seconds
            for connection, write, and pool, and 8 seconds for read to account
            for the API's 6 second processing limit. Pass None for no timeout.
        limits: Connection pool limits for the HTTP transport. Defaults to 20
            maximum connections with 10 keepalive connections. Keepalive
            connections expire after 30 seconds.

    Note:
        An API key can either be passed directly to the OpenAQ client class at
        instantiation or can be accessed from a system environment variable
        name `OPENAQ_API_KEY`. An API key added at instantiation will always
        override one set in the environment variable.

    Warning:
        Although the `api_key` parameter is not required for instantiating the
        OpenAQ client, an API Key is required for using the OpenAQ API.

    Raises:
        IdentifierOutOfBoundsError: Client validation error, identifier outside support int32 range.
        ApiKeyMissingError: Authentication error, missing API Key credentials.
        BadRequestError: Raised for HTTP 400 error, indicating a client request error.
        NotAuthorizedError: Raised for HTTP 401 error, indicating the client is not authorized.
        ForbiddenError: Raised for HTTP 403 error, indicating the request is forbidden.
        NotFoundError: Raised for HTTP 404 error, indicating a resource is not found.
        TimeoutError: Raised for HTTP 408 error, indicating the request has timed out.
        ValidationError: Raised for HTTP 422 error, indicating invalid request parameters.
        RateLimitError: Raised when rate limit exceeded and auto_wait is False.
        HTTPRateLimitError: Raised for HTTP 429 error, indicating rate limit exceeded.
        ServerError: Raised for HTTP 500 error, indicating an internal server error or unexpected server-side issue.
        BadGatewayError: Raised for HTTP 502, indicating that the gateway or proxy received an invalid response from the upstream server.
        ServiceUnavailableError: Raised for HTTP 503, indicating that the server is not ready to handle the request.
        GatewayTimeoutError: Raised for HTTP 504 error, indicating a gateway timeout.

    """

    _rate_limit_capacity: float
    _rate_limit_remaining: float
    _in_flight_requests: int
    _current_window_id: str
    _sync_in_progress: bool
    _lock: asyncio.Lock
    _rate_limit_synced_event: asyncio.Event

    def __init__(
        self,
        api_key: str | None = None,
        headers: Mapping[str, str] | None = None,
        auto_wait: bool = True,
        base_url: str = DEFAULT_BASE_URL,
        transport: AsyncTransport | None = None,
        timeout: float | httpx.Timeout | None = DEFAULT_TIMEOUT,
        limits: httpx.Limits = DEFAULT_LIMITS,
        rate_limit_override: int | None = None,
    ) -> None:
        if transport is None:
            transport = AsyncTransport(timeout=timeout, limits=limits)
        if headers is None:
            headers = {}
        super().__init__(transport, headers, api_key, auto_wait, base_url)
        self._user_agent = (
            f"openaq-python-async-{__version__}-{platform.python_version()}"
        )
        self.resolve_headers()
        self.countries = Countries(self)
        self.instruments = Instruments(self)
        self.licenses = Licenses(self)
        self.locations = Locations(self)
        self.manufacturers = Manufacturers(self)
        self.measurements = Measurements(self)
        self.owners = Owners(self)
        self.providers = Providers(self)
        self.parameters = Parameters(self)
        self.sensors = Sensors(self)
        rate_limit = rate_limit_override if rate_limit_override is not None else 60
        self._rate_limit_capacity = float(rate_limit)
        self._rate_limit_remaining = self._rate_limit_capacity
        self._lock = asyncio.Lock()
        self._in_flight_requests = 0
        self._current_window_id = datetime.now().strftime("%Y%m%d%H%M")
        self._rate_limit_synced_event = asyncio.Event()
        self._sync_in_progress = False

    @property
    def transport(self) -> AsyncTransport:
        return self._transport

    async def _acquire_token(self) -> None:
        """Acquire a rate limit token before making a request.

        Checks available capacity against in-flight requests in the current
        time window. If capacity is available, increments the in-flight counter
        and returns immediately. If the window has rolled over, resets remaining
        capacity accounting for any still in-flight requests from the previous
        window before granting the token.

        If no capacity is available and auto_wait is enabled, sleeps until the
        next window opens and then grants the token. If auto_wait is disabled,
        raises RateLimitError immediately.

        Raises:
            RateLimitError: If capacity is exhausted and auto_wait is False.
        """
        async with self._lock:
            now = datetime.now()
            window_id = now.strftime("%Y%m%d%H%M")

            if self._current_window_id != window_id:
                self._rate_limit_remaining = (
                    self._rate_limit_capacity - self._in_flight_requests
                )
                self._current_window_id = window_id

            available = self._rate_limit_remaining - self._in_flight_requests
            if available >= 1.0:
                self._in_flight_requests += 1
                return

            if not self._auto_wait:
                raise RateLimitError("Rate limit exceeded")

            seconds_until_next_min = 60 - now.second - (now.microsecond / 1_000_000)
            wait = seconds_until_next_min + 0.5

        await asyncio.sleep(wait)

        async with self._lock:
            self._rate_limit_remaining = (
                self._rate_limit_capacity - self._in_flight_requests
            )
            self._current_window_id = datetime.now().strftime("%Y%m%d%H%M")
            self._in_flight_requests += 1

    def _set_rate_limit(self, headers: httpx.Headers | Mapping[str, str]) -> None:
        """Synchronize local rate limit state with API provided response headers.

        Reads the x-ratelimit-remaining and x-ratelimit-limit headers from the
        HTTP response and updates the local capacity and remaining token counts.
        This corrects any drift between the client-side estimates and the
        server's actual counts, such as at window boundaries or after bursts.

        Args:
            headers: The response headers from the HTTP client.
        """
        x_ratelimit_remaining_header = headers.get("x-ratelimit-remaining")
        x_ratelimit_limit_header = headers.get("x-ratelimit-limit")

        try:
            if x_ratelimit_limit_header is not None:
                self._rate_limit_capacity = float(x_ratelimit_limit_header)
            if x_ratelimit_remaining_header is not None:
                self._rate_limit_remaining = float(x_ratelimit_remaining_header)
        except ValueError as e:
            logger.error(f"API sent malformed rate limit headers: {e}")

    async def _do(
        self,
        method: str,
        path: str,
        *,
        params: (
            httpx.QueryParams | Mapping[str, str | int | float | bool] | None
        ) = None,
        headers: httpx.Headers | Mapping[str, str] | None = None,
    ) -> httpx.Response:
        """Execute an HTTP request with rate limit handling and state synchronization.

        On the first request, designates the calling coroutine as the
        initial sync request. All other coroutines that arrive before the first
        response is received will wait until the server has confirmed the true
        rate limit state via response headers. Subsequent requests proceed
        directly to token acquisition.

        Once a token is acquired, builds the request headers, constructs the
        full URL, and dispatches the request via the transport layer. On
        completion, synchronizes local rate limit state from the response
        headers and decrements the in-flight counter.

        Args:
            method: HTTP method.
            path: API endpoint path.
            params: Query parameters.
            headers: Additional request headers.

        Returns:
            HTTP response object.

        Raises:
            RateLimitError: If rate limited and auto_wait is False.
        """
        is_initial_request = False
        if not self._rate_limit_synced_event.is_set():
            async with self._lock:
                if (
                    not self._rate_limit_synced_event.is_set()
                    and not self._sync_in_progress
                ):
                    self._sync_in_progress = True
                    is_initial_request = True

            if not is_initial_request:
                await self._rate_limit_synced_event.wait()

        await self._acquire_token()

        try:
            request_headers = self.build_request_headers(headers)
            url = self._base_url + path
            data = await self.transport.send_request(
                method=method, url=url, params=params, headers=request_headers
            )
            self._set_rate_limit(data.headers)
            return data

        finally:
            async with self._lock:
                self._in_flight_requests = max(0, self._in_flight_requests - 1)
                if is_initial_request:
                    self._sync_in_progress = False

            if is_initial_request:
                self._rate_limit_synced_event.set()

    async def _get(
        self,
        path: str,
        *,
        params: (
            httpx.QueryParams | Mapping[str, str | int | float | bool] | None
        ) = None,
        headers: httpx.Headers | Mapping[str, str] | None = None,
    ) -> httpx.Response:
        """Make a GET request to the API.

        Args:
            path: API endpoint path.
            params: Query parameters.
            headers: Additional request headers.

        Returns:
            HTTPX response object.
        """
        return await self._do("get", path, params=params, headers=headers)

    async def close(self) -> None:
        """Closes transport connection."""
        return await self.transport.close()

    async def __aenter__(self) -> AsyncOpenAQ:
        """Enter the async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the async context manager and close the connection."""
        await self.close()
