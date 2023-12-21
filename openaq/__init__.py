"""OpenAQ API Python wrapper."""

__version__ = "0.2.0"


from ._async.client import AsyncOpenAQ as AsyncOpenAQ
from ._sync.client import OpenAQ as OpenAQ
from .shared.exceptions import (
    AuthError,
    GatewayTimeoutError,
    NotAuthorized,
    NotFoundError,
    RateLimit,
    ValidationError,
    BadRequestError,
    Forbidden,
    ServerError,
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
