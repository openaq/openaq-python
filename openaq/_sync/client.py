from __future__ import annotations

import logging
from datetime import time
from types import TracebackType
from typing import Mapping

import httpx

from openaq._sync.models.countries import Countries
from openaq._sync.models.instruments import Instruments
from openaq._sync.models.licenses import Licenses
from openaq._sync.models.locations import Locations
from openaq._sync.models.manufacturers import Manufacturers
from openaq._sync.models.measurements import Measurements
from openaq._sync.models.owners import Owners
from openaq._sync.models.parameters import Parameters
from openaq._sync.models.providers import Providers
from openaq._sync.models.sensors import Sensors
from openaq.shared.client import DEFAULT_BASE_URL, BaseClient

from .transport import Transport

logger = logging.getLogger(__name__)


class OpenAQ(BaseClient[Transport]):
    """OpenAQ synchronous client.

    Args:
        api_key: The API key for accessing the service.
        headers: Additional headers to be sent with the request.
        auto_wait: Whether to automatically wait when rate limited. Defaults to True.
        base_url: The base URL for the API endpoint.
        _transport: The transport instance for making HTTP requests. For internal use.

    Note:
        An API key can either be passed directly to the OpenAQ client class at
        instantiation or can be accessed from a system environment variable
        named `OPENAQ_API_KEY`. An API key added at instantiation will always
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
        _transport: Transport = Transport(),
    ) -> None:
        super().__init__(_transport, headers, api_key, auto_wait, base_url)

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

    def _wait_for_rate_limit_reset(self) -> None:
        """Wait until the rate limit resets."""
        wait_seconds = self._rate_limit_reset_seconds
        if wait_seconds > 0:
            logger.info(f"Rate limit hit. Waiting {wait_seconds} seconds for reset.")
            time.sleep(wait_seconds)

    def _do(
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
            method: HTTP method (get, post, etc.).
            path: API endpoint path.
            params: Query parameters.
            headers: Additional request headers.

        Returns:
            HTTP response object.

        Raises:
            RateLimitError: If rate limited and auto_wait is False.
        """
        self._check_rate_limit()
        if self._auto_wait and self._is_rate_limited():
            self._wait_for_rate_limit_reset()
        request_headers = self.build_request_headers(headers)
        url = self._base_url + path
        data = self.transport.send_request(
            method=method, url=url, params=params, headers=request_headers
        )
        self._set_rate_limit(data.headers)
        return data

    def _get(
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
            headers: HTTP request headers.

        Returns:
            HTTP response object.
        """
        return self._do("get", path, params=params, headers=headers)

    def close(self) -> None:
        """Close the transport connection."""
        self.transport.close()

    def __enter__(self) -> OpenAQ:
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager and close the connection."""
        self.close()
