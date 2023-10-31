"""Base class and utilities to for shared client code."""

import platform
from abc import ABC, abstractmethod
from typing import Any, Mapping, Union

from openaq.shared.transport import BaseTransport

ACCEPT_HEADER = "application/json"

DEFAULT_USER_AGENT = f"openaq-python-{platform.python_version()}"


def resolve_headers(
    headers: Mapping[str, str],
    api_key: str,
    user_agent: str,
) -> Mapping[str, str]:
    """Resolves and updates the HTTP headers with the given API key and User Agent.

    Args:
        headers: The initial headers.
        api_key: The OpenAQ API key to be added as X-API-Key header.
        user_agent: The User-Agent header to be added.

    Returns:
        Updated headers with the added API key and User Agent.
    """
    headers["X-API-Key"] = api_key
    headers["User-Agent"] = user_agent
    headers["Accept"] = ACCEPT_HEADER
    return headers


class BaseClient(ABC):
    """Abstract class for OpenAQ clients.

    This class provides the basic structure and attributes for OpenAQ clients. It includes methods to
    interact with the OpenAQ API and handle HTTP headers.

    Attributes:
        _headers: The HTTP headers to include in requests.
        _transport: The transport instance to make requests.
        _base_url: The base URL of the OpenAQ API.

    Args:
        _transport: The transport instance to make requests.
        base_url: The base URL of the OpenAQ API. Defaults to "https://api.openaq.org/v3/".
    """

    def __init__(
        self,
        _transport: BaseTransport,
        _headers: Mapping[str, str] = {},
        base_url: str = "https://api.openaq.org/v3/",
    ) -> None:
        """Initialize a new instance of BaseClient.

        Args:
            _transport: The transport mechanism used for making requests to the OpenAQ API.
            base_url: The base URL for the OpenAQ API. Defaults to "https://api.openaq.org/v3/".
        """
        self._headers = _headers
        self._transport = _transport
        self._base_url = base_url

    @property
    def transport(self) -> BaseTransport:
        """Get the transport mechanism used by the client.

        Provides access to the transport instance that the client uses to
        communicate with the OpenAQ API.

        Returns:
            The transport instance.
        """
        return self._transport

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
