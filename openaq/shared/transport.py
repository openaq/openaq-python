"""Base class and utlity functions for working with client transport."""

from __future__ import annotations

import logging
from http import HTTPStatus

import httpx

from openaq.shared.exceptions import (
    BadGatewayError,
    BadRequestError,
    ForbiddenError,
    GatewayTimeoutError,
    TimeoutError,
    HTTPRateLimitError,
    NotAuthorizedError,
    NotFoundError,
    ServerError,
    ServiceUnavailableError,
    UnexpectedStatusCodeError,
    ValidationError,
)

logger = logging.getLogger("transport")


def check_response(res: httpx.Response) -> httpx.Response:
    """Checks the HTTP response of the request.

    Args:
        res: an httpx.Response object

    Returns:
        httpx.Response

    Raises:
        BadRequestError: Raised for HTTP 400 error, indicating a client request error.
        NotAuthorizedError: Raised for HTTP 401 error, indicating the client is not authorized.
        ForbiddenError: Raised for HTTP 403 error, indicating the request is forbidden.
        NotFoundError: Raised for HTTP 404 error, indicating a resource is not found.
        TimeoutError: Raised for HTTP 408 error, indicating the request has timed out.
        ValidationError: Raised for HTTP 422 error, indicating invalid request parameters.
        HTTPRateLimitError: Raised for HTTP 429 error, indicating rate limit exceeded.
        ServerError: Raised for HTTP 500 error, indicating an internal server error or unexpected server-side issue.
        BadGatewayError: Raised for HTTP 502, indicating that the gateway or proxy received an invalid response from the upstream server.
        ServiceUnavailableError: Raised for HTTP 503, indicating that the server is not ready to handle the request.
        GatewayTimeoutError: Raised for HTTP 504 error, indicating a gateway timeout.
    """
    logger.debug(f"HTTP {res.status_code}")
    if res.status_code >= HTTPStatus.OK and res.status_code < HTTPStatus.BAD_REQUEST:
        return res
    elif res.status_code == HTTPStatus.BAD_REQUEST:
        raise BadRequestError(res.text)
    elif res.status_code == HTTPStatus.NOT_FOUND:
        raise NotFoundError(res.text)
    elif res.status_code == HTTPStatus.REQUEST_TIMEOUT:
        raise TimeoutError(res.text)
    elif res.status_code == HTTPStatus.FORBIDDEN:
        raise ForbiddenError(res.text)
    elif res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        raise ValidationError(res.text)
    elif res.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        raise HTTPRateLimitError(res.text)
    elif res.status_code == HTTPStatus.UNAUTHORIZED:
        raise NotAuthorizedError(res.text)
    elif res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        raise ServerError(res.text)
    elif res.status_code == HTTPStatus.BAD_GATEWAY:
        raise BadGatewayError(res.text)
    elif res.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
        raise ServiceUnavailableError(res.text)
    elif res.status_code == HTTPStatus.GATEWAY_TIMEOUT:
        raise GatewayTimeoutError(
            "Your request timed out on the server. "
            "Consider reducing the complexity of your request."
        )
    else:
        logger.error(f"Unexpected HTTP status code {res.status_code}: {res.text}")
        raise UnexpectedStatusCodeError(f"HTTP {res.status_code}: {res.text}")
