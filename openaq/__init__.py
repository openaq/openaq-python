"""OpenAQ Python SDK."""

import logging

__version__ = "0.7.0"


logger = logging.getLogger(__name__)
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
