"""OpenAQ Python SDK."""

import logging

__version__ = "0.6.0"


logger = logging.getLogger("openaq")
logger.addHandler(logging.NullHandler())


from ._async.client import AsyncOpenAQ as AsyncOpenAQ
from ._sync.client import OpenAQ as OpenAQ
from .shared.exceptions import (
    ApiKeyMissingError,
    IdentifierOutOfBoundsError,
    BadGatewayError,
    BadRequestError,
    ForbiddenError,
    GatewayTimeoutError,
    HTTPRateLimitError,
    NotAuthorizedError,
    NotFoundError,
    TimeoutError,
    RateLimitError,
    ServiceUnavailableError,
    ServerError,
    ValidationError,
)

__all__ = [
    "OpenAQ",
    "AsyncOpenAQ",
    "IdentifierOutOfBoundsError",
    "ApiKeyMissingError",
    "NotAuthorizedError",
    "NotFoundError",
    "TimeoutError",
    "ValidationError",
    "GatewayTimeoutError",
    "HTTPRateLimitError",
    "RateLimitError",
    "BadRequestError",
    "ForbiddenError",
    "ServerError",
    "ServiceUnavailableError",
    "BadGatewayError",
]
