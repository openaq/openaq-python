"""Custom exceptions to catch various HTTP codes returned by the OpenAQ API."""


class ClientError(Exception):
    """Base class for all client exceptions."""

    pass


class AuthError(ClientError):
    """Authentication error, improperly supplied credentials."""

    pass


class BadRequestError(ClientError):
    """HTTP 400 - Client request error.

    Attributes:
        status: HTTP status code
    """

    status: int = 400


class NotAuthorizedError(AuthError):
    """HTTP 401- Not authorized.

    Attributes:
        status: HTTP status code
    """

    status: int = 401


class ForbiddenError(AuthError):
    """HTTP 403 - Forbidden.

    Attributes:
        status: HTTP status code
    """

    status: int = 403


class NotFoundError(ClientError):
    """HTTP 404 - Resource not found.

    Attributes:
        status: HTTP status code
    """

    status: int = 404


class ValidationError(BadRequestError):
    """HTTP 422 - Client request with invalid parameters.

    Attributes:
        status: HTTP status code
    """

    status: int = 422


class RateLimitError(ClientError):
    """Exception for catching rate limit exceedances from client.

    Attributes:
        message:
    """

    def __init__(self, time_remaining: int):
        self.message = f"Rate limit exceeded. Limit resets in {time_remaining} seconds"


class HTTPRateLimitError(ClientError):
    """HTTP 429 - Client request exceeds rate limits.

    Attributes:
        status: HTTP status code
    """

    status: int = 429


class ServerError(Exception):
    """HTTP 500 - Server or service failure.

    Attributes:
        status: HTTP status code
    """

    status: int = 500


class GatewayTimeoutError(ServerError):
    """HTTP 504 - Timeout from the gateway after failing to route request to destination service.

    Attributes:
        status: HTTP status code
    """

    status: int = 504
