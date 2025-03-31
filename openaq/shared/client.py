"""Base class and utilities to for shared client code."""

from __future__ import annotations

import logging
import math
import os
import platform
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Generic, Mapping, TypeVar

import httpx

from openaq.shared.exceptions import ApiKeyMissingError, RateLimitError

logger = logging.getLogger('openaq')

# for Python versions <3.11 tomllib is not part of std. library
_has_toml = True
try:
    import tomllib
except ImportError:
    _has_toml = False

from openaq import __version__

ACCEPT_HEADER = "application/json"

DEFAULT_USER_AGENT = f"openaq-python-{__version__}-{platform.python_version()}"

DEFAULT_BASE_URL = "https://api.openaq.org/v3/"

TTransport = TypeVar('TTransport')


class BaseClient(ABC, Generic[TTransport]):
    """Abstract class for OpenAQ clients.

    This class provides the basic structure and attributes for OpenAQ clients. It includes methods to
    interact with the OpenAQ API and handle HTTP headers.

    Attributes:
        _headers: The HTTP headers to include in requests.
        _transport: The transport instance to make requests.
        _api_key: API key
        _user_agent: User-Agent HTTP header
        _base_url: The base URL of the OpenAQ API.

    Args:
        transport: The transport mechanism used for making requests to the OpenAQ API.
        headers: mapping of HTTP headers to be sent with request.
        api_key: OpenAQ API key string.
        user_agent: User-Agent header value to be sent with HTTP requests.
        base_url: The base URL for the OpenAQ API. Defaults to "https://api.openaq.org/v3/".
    """

    _api_key: str | None

    def __init__(
        self,
        transport: TTransport,
        headers: Mapping[str, str] = {},
        api_key: str | None = None,
        base_url: str = "https://api.openaq.org/v3/",
    ) -> None:
        """Initialize a new instance of BaseClient.

        Args:
            transport: The transport mechanism used for making requests to the OpenAQ API.
            headers: mapping of HTTP headers to be sent with request.
            api_key: OpenAQ API key string.
            user_agent: User-Agent header value to be sent with HTTP requests.
            base_url: The base URL for the OpenAQ API. Defaults to "https://api.openaq.org/v3/".
        """
        if api_key:
            self._api_key = api_key
        else:
            self._api_key = self._get_api_key()
        self._headers = headers
        self._transport = transport
        self._base_url = base_url
        self._user_agent = DEFAULT_USER_AGENT
        self.resolve_headers()
        self._rate_limit_reset_datetime = datetime.min
        self._rate_limit_remaining = math.inf
        self._check_api_key_url()

    def _check_api_key_url(self):
        if not self.api_key and self.base_url == DEFAULT_BASE_URL:
            logger.error(
                "API key not set: An API key is required when using the OpenAQ API"
            )
            raise ApiKeyMissingError(
                "API key not set: An API key is required when using the OpenAQ API"
            )

    def _get_api_key(self) -> str | None:
        """Gets API key value from env or openaq config file.

        Returns:
            The API key value set either in the `OPENAQ_API_KEY` environment
            variable or the `api-key` value in the .openaq.toml configuration
            file. A value passed to the `api_key` parameter in the class
            constructor will always override these other values. the
            `OPENAQ_API_KEY` environment variable get second priority with
            the configuration file `api-key` having last priority.
        """
        if os.environ.get("OPENAQ_API_KEY", None):
            return os.environ.get("OPENAQ_API_KEY")
        config = _get_openaq_config()
        if config:
            return config.get('api-key')
        return None

    @property
    def api_key(self) -> str | None:
        """Accessor for private _api_key field.

        Returns:
            The API key string.
        """
        return self._api_key

    @property
    def transport(self) -> TTransport:
        """Get the transport mechanism used by the client.

        Provides access to the transport instance that the client uses to
        communicate with the OpenAQ API.

        Returns:
            The transport instance.
        """
        return self._transport

    @property
    def headers(self) -> Mapping[str, str]:
        """Accessor for private _headers field.

        Returns:
            dictionary of http headers to be sent with request
        """
        return self._headers

    def build_request_headers(self, headers: Mapping[str, str] | None = None) -> dict:
        """Copies and updates headers based on input.

        Args:
            headers: The headers to add to the request.

        Returns:
            A mapping of headers for the request
        """
        if headers:
            request_headers = {k: v for k, v in self._headers.items()}
            request_headers = request_headers.copy()
            request_headers.update(headers)
        else:
            request_headers = {k: v for k, v in self._headers.items()}
        return request_headers

    @property
    def base_url(self) -> str:
        """Accessor for private _base_url field.

        Returns:
            base URL string value

        """
        return self._base_url

    def resolve_headers(self):
        """Resolves and updates the HTTP headers with the given API key and User Agent.

        Args:
            headers: The initial headers.
            api_key: The OpenAQ API key to be added as X-API-Key header.
            user_agent: The User-Agent header to be added.

        Returns:
            Updated headers with the added API key and User Agent.
        """
        self._headers["X-API-Key"] = self.api_key
        self._headers["User-Agent"] = self._user_agent
        self._headers["Accept"] = ACCEPT_HEADER

    @abstractmethod
    def close(self):
        """Closes transport connection."""
        raise NotImplementedError

    @abstractmethod
    def _do(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def _get(
        self,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, Any] | None = None,
    ):
        raise NotImplementedError

    def _is_rate_limited(self) -> bool:
        return (
            self._rate_limit_remaining == 0
            and self._rate_limit_reset_datetime > datetime.now()
        )

    def _check_rate_limit(self):
        if self._is_rate_limited():
            logger.exception(f"Rate limit exceeded")
            message = f"Rate limit exceeded. Limit resets in {self._rate_limit_reset_seconds} seconds"
            raise RateLimitError(message)

    @property
    def _rate_limit_reset_seconds(self):
        return int((self._rate_limit_reset_datetime - datetime.now()).total_seconds())

    def _set_rate_limit(self, headers: httpx.Headers):
        rate_limit_remaining = int(headers.get('x-ratelimit-remaining', 0))
        rate_limit_reset_seconds = int(headers.get('x-ratelimit-reset', 60))
        now = (datetime.now() + timedelta(seconds=0.5)).replace(microsecond=0)
        rate_limit_reset_datetime = now + timedelta(seconds=rate_limit_reset_seconds)
        self._rate_limit_remaining = rate_limit_remaining
        self._rate_limit_reset_datetime = rate_limit_reset_datetime


def _get_openaq_config() -> Mapping[str, str] | None:
    """Reads .openaq.toml configuration file.

    Depends on tomllib so only available in Python >3.11.

    """
    config_path = Path(Path.home() / ".openaq.toml")
    if config_path.is_file():
        with open(config_path, 'rb') as f:
            if _has_toml:
                config = tomllib.load(f)
            else:
                config = None
            return config
    return None
