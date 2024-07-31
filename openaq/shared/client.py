"""Base class and utilities to for shared client code."""

import os
import platform
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Mapping, Union

# for Python versions <3.11 tomllib is not part of std. library
_has_toml = True
try:
    import tomllib
except ImportError:
    _has_toml = False

from openaq import __version__
from openaq.shared.transport import BaseTransport

ACCEPT_HEADER = "application/json"

DEFAULT_USER_AGENT = f"openaq-python-{__version__}-{platform.python_version()}"

DEFAULT_BASE_URL = "https://api.openaq.org/v3/"


class BaseClient(ABC):
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
        _transport: The transport mechanism used for making requests to the OpenAQ API.
        _headers: mapping of HTTP headers to be sent with request.
        api_key: OpenAQ API key string.
        user_agent: User-Agent header value to be sent with HTTP requests.
        base_url: The base URL for the OpenAQ API. Defaults to "https://api.openaq.org/v3/".
    """

    def __init__(
        self,
        _transport: BaseTransport,
        user_agent: str,
        base_url: str,
        _headers: Mapping[str, str] = {},
        api_key: Union[str, None] = None,
        base_url: str = "https://api.openaq.org/v3/",
    ) -> None:
        """Initialize a new instance of BaseClient.

        Args:
            _transport: The transport mechanism used for making requests to the OpenAQ API.
            _headers: mapping of HTTP headers to be sent with request.
            api_key: OpenAQ API key string.
            user_agent: User-Agent header value to be sent with HTTP requests.
            base_url: The base URL for the OpenAQ API. Defaults to "https://api.openaq.org/v3/".
        """

        if api_key:
            self.api_key = api_key
        else:
            self.api_key = self._api_key()
        self.__headers = _headers
        self.__transport = _transport
        self.__base_url = base_url
        self.__user_agent = user_agent

    def _api_key(self) -> str:
        """Gets API key value from env or openaq config file.

        Returns:
            The API key value set either in the `OPENAQ_API_KEY` environment
            variable or the `api-key` value in the .openaq.toml configutation
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

    @property
    def transport(self) -> BaseTransport:
        """Get the transport mechanism used by the client.

        Provides access to the transport instance that the client uses to
        communicate with the OpenAQ API.

        Returns:
            The transport instance.
        """
        return self.__transport

    @property
    def headers(self) -> Mapping[str, str]:
        """Accessor for private __headers field.

        Returns:
            dictionary of http headers to be sent with request
        """
        return self.__headers

    @property
    def api_key(self) -> Union[str, None]:
        """Access for private __api_key field.

        Returns:
            API key value
        """
        return self.__api_key

    @property
    def base_url(self) -> str:
        """Accessor for private __base_url field.

        Returns:
            base URL string value

        """
        return self.__base_url

    @staticmethod
    def _set_api_key():
        """Sets API key from environment variable."""
        api_key = os.environ.get('OPENAQ-API-KEY', None)
        return api_key

    def resolve_headers(self):
        """Resolves and updates the HTTP headers with the given API key and User Agent.

        Args:
            headers: The initial headers.
            api_key: The OpenAQ API key to be added as X-API-Key header.
            user_agent: The User-Agent header to be added.

        Returns:
            Updated headers with the added API key and User Agent.
        """
        self.__headers["X-API-Key"] = self.__api_key
        self.__headers["User-Agent"] = self.__user_agent
        self.__headers["Accept"] = ACCEPT_HEADER

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
        params: Union[Mapping[str, Any], None] = None,
        headers: Union[Mapping[str, str], None] = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def _get(
        self,
        path: str,
        *,
        params: Union[Mapping[str, str], None] = None,
        headers: Union[Mapping[str, Any], None] = None,
    ):
        raise NotImplementedError


def _get_openaq_config() -> Union[Mapping[str, str], None]:
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
