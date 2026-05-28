"""OpenAQ Python SDK."""

import logging

__version__ = "1.0.0rc4"


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


from .client import OpenAQ as OpenAQ
from .core.exceptions import (
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
