"""Base class and utlity functions for working with client transport."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any, Mapping

from httpx import Response

from openaq.shared.exceptions import (
    BadGatewayError,
    BadRequestError,
    ForbiddenError,
    GatewayTimeoutError,
    HTTPRateLimitError,
    NotAuthorizedError,
    NotFoundError,
    ServerError,
    ServiceUnavailableError,
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


def check_response(res: Response) -> Response | None:
    """Checks the HTTP response of the request.

    Args:
        res: an httpx.Response object

    Returns:
        httpx.Response

    Raises:
        AuthError: Authentication error, improperly supplied credentials.
        BadRequestError: Raised for HTTP 400 error, indicating a client request error.
        NotAuthorizedError: Raised for HTTP 401 error, indicating the client is not authorized.
        ForbiddenError: Raised for HTTP 403 error, indicating the request is forbidden.
        NotFoundError: Raised for HTTP 404 error, indicating a resource is not found.
        ValidationError: Raised for HTTP 422 error, indicating invalid request parameters.
        HTTPRateLimitError: Raised for HTTP 429 error, indicating rate limit exceeded.
        ServerError: Raised for HTTP 500 error, indicating an internal server error or unexpected server-side issue.
        BadGatewayError: Raised for HTTP 502, indicating that the gateway or proxy received an invalid response from the upstream server.
        ServiceUnavailableError: Raised for HTTP 503, indicating that the server is not ready to handle the request.
        GatewayTimeoutError: Raised for HTTP 504 error, indicating a gateway timeout.
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
        raise ForbiddenError(res.text)
    elif res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise ValidationError(res.text)
    elif res.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise HTTPRateLimitError(res.text)
    elif res.status_code == HTTPStatus.UNAUTHORIZED:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise NotAuthorizedError(res.text)
    elif res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise ServerError(res.text)
    elif res.status_code == HTTPStatus.BAD_GATEWAY:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise BadGatewayError(res.text)
    elif res.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise ServiceUnavailableError(res.text)
    elif res.status_code == HTTPStatus.GATEWAY_TIMEOUT:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise GatewayTimeoutError(
            "Your request timed out on the server. "
            "Consider reducing the complexity of your request."
        )
    else:
        logger.exception(f"HTTP {res.status_code} - {res.text}")
        raise Exception
