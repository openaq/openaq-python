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


class NotAuthorized(AuthError):
    """HTTP 401- Not authorized.

    Attributes:
        status: HTTP status code
    """

    status: int = 401


class Forbidden(AuthError):
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


class RateLimit(ClientError):
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
