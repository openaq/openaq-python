from __future__ import annotations

import asyncio
import logging
from types import TracebackType
from typing import Mapping

import httpx

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

from .transport import AsyncTransport

logger = logging.getLogger(__name__)


class AsyncOpenAQ(BaseClient[AsyncTransport]):
    """OpenAQ asynchronous client.

    Args:
        api_key: The API key for accessing the service.
        headers: Additional headers to be sent with the request.
        auto_wait: Whether to automatically wait when rate limited. Defaults to True.
        base_url: The base URL for the API endpoint.
        _transport: The transport instance for making HTTP requests. For internal use.

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

    def __init__(
        self,
        api_key: str | None = None,
        headers: Mapping[str, str] = {},
        auto_wait: bool = True,
        base_url: str = DEFAULT_BASE_URL,
        transport: AsyncTransport = AsyncTransport(),
    ) -> None:
        super().__init__(transport, headers, api_key, auto_wait, base_url)

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

    @property
    def transport(self) -> AsyncTransport:
        return self._transport

    async def _wait_for_rate_limit_reset(self) -> None:
        """Wait asynchronously until the rate limit resets."""
        wait_seconds = self._rate_limit_reset_seconds
        if wait_seconds > 0:
            logger.info(f"Rate limit hit. Waiting {wait_seconds} seconds for reset...")
            await asyncio.sleep(wait_seconds)

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
        """Execute an HTTP request with rate limit handling.

        Checks rate limits before making the request. If auto_wait is enabled
        and rate limited, waits for the limit to reset. Otherwise raises
        RateLimitError if rate limited.

        Args:
            method: HTTP method.
            path: API endpoint path.
            params: Query parameters.
            headers: HTTP request headers.

        Returns:
            HTTP response object.

        Raises:
            RateLimitError: If rate limited and auto_wait is False.
        """
        self._check_rate_limit()

        if self._auto_wait and self._is_rate_limited():
            await self._wait_for_rate_limit_reset()

        request_headers = self.build_request_headers(headers)
        url = self._base_url + path
        data = await self.transport.send_request(
            method=method, url=url, params=params, headers=request_headers
        )
        return data

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
