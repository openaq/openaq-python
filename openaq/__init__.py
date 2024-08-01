"""OpenAQ Python SDK."""

__version__ = "0.3.0"


from ._async.client import AsyncOpenAQ as AsyncOpenAQ
from ._sync.client import OpenAQ as OpenAQ
from .shared.exceptions import (
    AuthError,
    BadRequestError,
    Forbidden,
    GatewayTimeoutError,
    NotAuthorized,
    NotFoundError,
    RateLimit,
    ServerError,
    ValidationError,
)

__all__ = [
    "OpenAQ",
    "AsyncOpenAQ",
    "AuthError",
    "NotAuthorized",
    "NotFoundError",
    "ValidationError",
    "GatewayTimeoutError",
    "RateLimit",
    "BadRequestError",
    "Forbidden",
    "ServerError",
]
