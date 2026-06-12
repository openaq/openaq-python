"""OpenAQ API client for interacting with the OpenAQ REST API.

Provides the OpenAQ client class which manages authentication, connection
pooling, and rate limiting for requests to the OpenAQ API.
"""

from __future__ import annotations

import logging
import os
import platform
import time
from collections.abc import Mapping
from datetime import datetime, timedelta
from pathlib import Path
from types import TracebackType
from urllib.parse import urljoin, urlparse

from openaq import __version__
from openaq.core.exceptions import ApiKeyMissingError, RateLimitError
from openaq.core.transport import (
    DEFAULT_LIMITS,
    DEFAULT_TIMEOUT,
    Headers,
    Response,
    Transport,
)
from openaq.models.countries import Countries
from openaq.models.instruments import Instruments
from openaq.models.licenses import Licenses
from openaq.models.locations import Locations
from openaq.models.manufacturers import Manufacturers
from openaq.models.measurements import Measurements
from openaq.models.owners import Owners
from openaq.models.parameters import Parameters
from openaq.models.providers import Providers
from openaq.models.sensors import Sensors

logger = logging.getLogger(__name__)

ACCEPT_HEADER = "application/json"
DEFAULT_BASE_URL = "https://api.openaq.org/v3/"

# for Python versions <3.11 tomllib is not part of std. library
_has_toml = True
try:
    import tomllib
except ModuleNotFoundError:
    _has_toml = False


def _get_openaq_config() -> dict[str, str] | None:
    """Read api_key from ~/.config/openaq/config.toml if present."""
    config_path = Path.home() / ".config" / "openaq" / "config.toml"
    if config_path.is_file():
        with open(config_path, "rb") as f:
            if _has_toml:
                raw = tomllib.load(f)
                api_key = raw.get("api-key")
                if isinstance(api_key, str):
                    return {"api_key": api_key}
    return None


def _resolve_api_key(api_key: str | None) -> str | None:
    """Return api_key from argument, environment, or config file — in that order."""
    if api_key:
        return api_key
    if env := os.environ.get("OPENAQ_API_KEY"):
        return env
    if config := _get_openaq_config():
        return config["api_key"]
    return None


class OpenAQ:
    """OpenAQ API client.

    Args:
        api_key: The API key for accessing the service.
        headers: Additional headers to be sent with the request.
        auto_wait: Whether to automatically wait when rate limited. Defaults to
            True.
        base_url: The base URL for the API endpoint.
        _transport: The transport instance for making HTTP requests. For internal
            use.
        rate_limit_override: Override the default rate limit capacity of 60
            requests per minute. Useful for accounts with a higher rate limit.
            Defaults to None.

    Note:
        An API key can either be passed directly to the OpenAQ client class at
        instantiation or can be accessed from a system environment variable
        named `OPENAQ_API_KEY`. An API key added at instantiation will always
        override one set in the environment variable.

    Warning:
        Although the `api_key` parameter is not required for instantiating the
        OpenAQ client, an API Key is required for using the OpenAQ API.

    Raises:
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

    _rate_limit_reset_datetime: datetime
    _rate_limit_remaining: float
    _rate_limit_capacity: float

    def __init__(
        self,
        api_key: str | None = None,
        headers: Mapping[str, str] | None = None,
        auto_wait: bool = True,
        base_url: str = DEFAULT_BASE_URL,
        _transport: Transport | None = None,  # internal use only
        rate_limit_override: int | None = None,
    ) -> None:
        """Initializes the OpenAQ client.

        Args:
            api_key: The API key for accessing the service. If not provided,
                the client will attempt to resolve it from the OPENAQ_API_KEY
                environment variable or ~/.openaq.toml config file.
            headers: Additional headers to be sent with every request.
            auto_wait: Whether to automatically wait when rate limited. Defaults
                to True.
            base_url: The base URL for the API endpoint.
            _transport: The transport instance for making HTTP requests. For
                internal use.
            rate_limit_override: Initial rate limit capacity in requests per
                minute. Defaults to 60 and is corrected automatically from
                server response headers after the first request.

        Raises:
            ApiKeyMissingError: If no API key is provided and the default base
                URL is used.
        """
        self._api_key = _resolve_api_key(api_key)
        parsed = urlparse(base_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(
                f"Invalid base_url, must be a fully qualified URL: {base_url!r}"
            )
        self._base_url = parsed.geturl()
        self._auto_wait = auto_wait
        self._transport = (
            _transport
            if _transport is not None
            else Transport(timeout=DEFAULT_TIMEOUT, limits=DEFAULT_LIMITS)
        )
        self._headers = Headers(headers or {})

        if not self._api_key and self._base_url == DEFAULT_BASE_URL:
            logger.error(
                "API key not set: An API key is required when using the OpenAQ API"
            )
            raise ApiKeyMissingError(
                "API key not set: An API key is required when using the OpenAQ API"
            )

        self._user_agent = f"openaq-python-{__version__}-{platform.python_version()}"
        if self._api_key:
            self._headers["X-API-Key"] = self._api_key
        self._headers["User-Agent"] = self._user_agent
        self._headers["Accept"] = ACCEPT_HEADER

        # assumes default until corrected by the first response
        rate_limit = rate_limit_override if rate_limit_override is not None else 60
        self._rate_limit_capacity = float(rate_limit)
        self._rate_limit_reset_datetime = datetime.min
        self._rate_limit_remaining = self._rate_limit_capacity

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
    def api_key(self) -> str | None:
        """The API key used to authenticate requests."""
        return self._api_key

    @property
    def transport(self) -> Transport:
        """The transport instance used to send HTTP requests."""
        return self._transport

    @property
    def headers(self) -> Headers:
        """The default headers sent with every request."""
        return self._headers

    @property
    def base_url(self) -> str:
        """The base URL for the API."""
        return self._base_url

    @property
    def _rate_limit_reset_seconds(self) -> int:
        """Seconds remaining until the rate limit window resets."""
        return int((self._rate_limit_reset_datetime - datetime.now()).total_seconds())

    def _is_rate_limited(self) -> bool:
        """Returns True if the rate limit is exhausted and the reset time has not yet passed."""
        return (
            self._rate_limit_remaining <= 0
            and self._rate_limit_reset_datetime > datetime.now()
        )

    def _check_rate_limit(self) -> None:
        """Checks the current rate limit state before sending a request.

        If the rate limit is exhausted and the reset time has not passed,
        either waits for the reset if auto_wait is True, or raises
        RateLimitError if auto_wait is False. Decrements the remaining
        count by one after passing the check.

        Raises:
            RateLimitError: If rate limited and auto_wait is False.
        """
        if self._is_rate_limited():
            if self._auto_wait:
                self._wait_for_rate_limit_reset()
                self._rate_limit_remaining = self._rate_limit_capacity
            else:
                logger.error(
                    "Rate limit exceeded. Limit resets in %s seconds",
                    self._rate_limit_reset_seconds,
                )
                raise RateLimitError(
                    f"Rate limit exceeded. Limit resets in {self._rate_limit_reset_seconds} seconds"
                )
        self._rate_limit_remaining -= 1

    def _set_rate_limit(self, headers: Headers) -> None:
        """Updates rate limit state from response headers.

        Reads x-ratelimit-limit, x-ratelimit-remaining, and x-ratelimit-reset
        from the response headers to keep the client's local rate limit state
        in sync with the server.

        Args:
            headers: The response headers from a completed request.
        """
        rate_limit_capacity = self._get_int_header(headers, "x-ratelimit-limit", 60)
        rate_limit_remaining = self._get_int_header(headers, "x-ratelimit-remaining", 0)
        rate_limit_reset_seconds = self._get_int_header(
            headers, "x-ratelimit-reset", 60
        )
        now = (datetime.now() + timedelta(seconds=0.5)).replace(microsecond=0)
        self._rate_limit_capacity = float(rate_limit_capacity)
        self._rate_limit_remaining = rate_limit_remaining
        self._rate_limit_reset_datetime = now + timedelta(
            seconds=rate_limit_reset_seconds
        )

    def _wait_for_rate_limit_reset(self) -> None:
        """Blocks until the rate limit window resets.

        If the reset time is in the future, sleeps for the remaining duration.
        Returns immediately if the reset time has already passed.
        """
        wait_seconds = self._rate_limit_reset_seconds
        if wait_seconds > 0:
            logger.info("Rate limit hit. Waiting %s seconds for reset.", wait_seconds)
            time.sleep(wait_seconds)

    def _get_int_header(self, headers: Headers, key: str, default: int) -> int:
        """Reads an integer value from response headers with a fallback default.

        Args:
            headers: The response headers to read from.
            key: The header name to look up.
            default: The value to return if the header is missing or not a
                valid integer.

        Returns:
            The integer value of the header, or default if not present or invalid.
        """
        try:
            value = headers.get(key)
            if value is None:
                return default
            return int(value)
        except ValueError:
            return default

    def _build_request_headers(self, headers: Mapping[str, str] | None) -> Headers:
        """Merges per-request headers with the client's default headers.

        Args:
            headers: Optional additional headers for this request. If None,
                a copy of the default headers is returned.

        Returns:
            A Headers instance combining default and per-request headers.
        """
        if headers:
            request_headers = self._headers.copy()
            request_headers.update(headers)
            return request_headers
        return self._headers.copy()

    def _do(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str | int | float | bool] | None = None,
        headers: Headers | Mapping[str, str] | None = None,
    ) -> Response:
        """Execute an HTTP request with rate limit handling.

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
        request_headers = self._build_request_headers(headers)
        url = urljoin(self._base_url, path.lstrip("/"))
        data = self._transport.send_request(
            method=method, url=url, params=params, headers=request_headers
        )
        self._set_rate_limit(data.headers)
        return data

    def _get(
        self,
        path: str,
        *,
        params: Mapping[str, str | int | float | bool] | None = None,
        headers: Headers | Mapping[str, str] | None = None,
    ) -> Response:
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
        """Closes the transport and releases all pooled connections."""
        self._transport.close()

    def __enter__(self) -> OpenAQ:
        """Enters the context manager, returning the client instance."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exits the context manager, closing the transport."""
        self.close()
