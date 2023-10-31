"""OpenAQ API Python wrapper."""

__version__ = "0.1.1"


from ._async.client import AsyncOpenAQ as AsyncOpenAQ
from ._sync.client import OpenAQ as OpenAQ
from .shared.exceptions import (
    AuthError,
    GatewayTimeoutError,
    NotAuthorized,
    NotFoundError,
    RateLimit,
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
]
