"""Base class and utilities to for shared client code."""

import platform
from abc import ABC, abstractmethod
import os
from typing import Any, Mapping, Union

from openaq.shared.transport import BaseTransport

ACCEPT_HEADER = "application/json"

DEFAULT_USER_AGENT = f"openaq-python-{platform.python_version()}"

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
    ) -> None:
        """Initialize a new instance of BaseClient.

        Args:
            _transport: The transport mechanism used for making requests to the OpenAQ API.
            _headers: mapping of HTTP headers to be sent with request.
            api_key: OpenAQ API key string.
            user_agent: User-Agent header value to be sent with HTTP requests.
            base_url: The base URL for the OpenAQ API. Defaults to "https://api.openaq.org/v3/".
        """
        self.__headers = _headers
        self.__transport = _transport
        self.__base_url = base_url
        self.__api_key = api_key or self._set_api_key()
        self.__user_agent = user_agent

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
