"""OpenAQ Python SDK."""

__version__ = "1.1.0"

import logging

from .client import OpenAQ
from .core.exceptions import (
    ApiKeyMissingError,
    BadGatewayError,
    BadRequestError,
    ForbiddenError,
    GatewayTimeoutError,
    HTTPRateLimitError,
    IdentifierOutOfBoundsError,
    InvalidParameterError,
    NotAuthorizedError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
    TimeoutError,
    ValidationError,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__all__ = [
    "OpenAQ",
    "IdentifierOutOfBoundsError",
    "ApiKeyMissingError",
    "NotAuthorizedError",
    "NotFoundError",
    "TimeoutError",
    "InvalidParameterError",
    "ValidationError",
    "GatewayTimeoutError",
    "HTTPRateLimitError",
    "RateLimitError",
    "BadRequestError",
    "ForbiddenError",
    "ServerError",
    "ServiceUnavailableError",
    "BadGatewayError",
    "__version__",
]
