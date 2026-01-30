"""OpenAQ Python SDK."""

import logging

__version__ = "1.0.0rc"


logger = logging.getLogger("openaq")
logger.addHandler(logging.NullHandler())


from ._async.client import AsyncOpenAQ as AsyncOpenAQ
from ._sync.client import OpenAQ as OpenAQ
from .shared.exceptions import (
    ApiKeyMissingError,
    BadGatewayError,
    BadRequestError,
    ForbiddenError,
    GatewayTimeoutError,
    HTTPRateLimitError,
    IdentifierOutOfBoundsError,
    NotAuthorizedError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
    TimeoutError,
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
