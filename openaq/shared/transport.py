"""Base class and utlity functions for working with client transport."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any, Mapping, Union

from httpx import Response

from openaq.shared.exceptions import (
    BadRequestError,
    Forbidden,
    GatewayTimeoutError,
    NotAuthorized,
    NotFoundError,
    RateLimit,
    ServerError,
    ValidationError,
)

logger = logging.getLogger("transport")


class BaseTransport(ABC):
    """Base class for client transport classes."""

    @abstractmethod
    async def send_request(
        self,
        method: str,
        url: str,
        params: Mapping[str, str],
        headers: Mapping[str, Any],
    ):
        """Sends request using transport. To be overridden in subclass.

        Args:
            method: HTTP method name
            url: URL to send requestion to
            params: query parameters to add to URL
            headers: HTTP headers to include wiht request
        """
        raise NotImplementedError

    @abstractmethod
    async def close(self):
        """Closes transport connection. To be overridden in subclass."""
        raise NotImplementedError


def check_response(res: Response) -> Union[Response, None]:
    """Checks the HTTP response of the request.

    Args:
        res: an httpx.Response object


    Returns:
        httpx.Response

    Raises:
        BadRequestError:
        NotFoundError:
        ValidationError:
        RateLimitError:
        NotAuthorized:
        RateLimitError:
        GatewayTimeoutError:
    """
    if res.status_code >= HTTPStatus.OK and res.status_code < HTTPStatus.BAD_REQUEST:
        return res
    elif res.status_code == HTTPStatus.BAD_REQUEST:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise BadRequestError(res.text)
    elif res.status_code == HTTPStatus.NOT_FOUND:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise NotFoundError(res.text)
    elif res.status_code == HTTPStatus.FORBIDDEN:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise Forbidden(res.text)
    elif res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise ValidationError(res.text)
    elif res.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise RateLimit(res.text)
    elif res.status_code == HTTPStatus.UNAUTHORIZED:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise NotAuthorized(res.text)
    elif res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise ServerError(res.text)
    elif res.status_code == HTTPStatus.GATEWAY_TIMEOUT:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise GatewayTimeoutError(
            "Your request timed out on the server. "
            "Consider reducing the complexity of your request."
        )
    else:
        raise Exception
