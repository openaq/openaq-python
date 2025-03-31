"""Custom exceptions to catch various HTTP codes returned by the OpenAQ API."""

from typing import Literal


class ClientError(Exception):
    """Base class for all client exceptions."""

    pass


class AuthError(ClientError):
    """Authentication error, improperly supplied credentials."""

    pass


class ApiKeyMissingError(AuthError):
    """API Key missing error."""

    pass


class BadRequestError(ClientError):
    """HTTP 400 - Client request error.

    Attributes:
        status_code: HTTP status code
    """

    status_code: int = 400


class NotAuthorizedError(AuthError):
    """HTTP 401- Not authorized.

    Attributes:
        status_code: HTTP status code
    """

    status_code: Literal[401] = 401


class ForbiddenError(AuthError):
    """HTTP 403 - Forbidden.

    Attributes:
        status_code: HTTP status code
    """

    status_code: Literal[403] = 403


class NotFoundError(ClientError):
    """HTTP 404 - Resource not found.

    Attributes:
        status_code: HTTP status code
    """

    status_code: Literal[404] = 404


class ValidationError(BadRequestError):
    """HTTP 422 - Client request with invalid parameters.

    Attributes:
        status_code: HTTP status code
    """

    status_code: Literal[422] = 422


class RateLimitError(ClientError):
    """Exception for catching rate limit exceedances from client."""


class HTTPRateLimitError(ClientError):
    """HTTP 429 - Client request exceeds rate limits.

    Attributes:
        status_code: HTTP status code
    """

    status_code: Literal[429] = 429


class ServerError(Exception):
    """HTTP 500 - Server or service failure.

    Attributes:
        status_code: HTTP status code
    """

    status_code: int = 500


class BadGatewayError(ServerError):
    """HTTP 502 - Indicates that the gateway or proxy received an invalid response from the upstream server.

    Attributes:
        status_code: HTTP status code
    """

    status_code: Literal[502] = 502


class ServiceUnavailableError(ServerError):
    """HTTP 503 - Indicates that the server is not ready to handle the request.

    Attributes:
        status_code: HTTP status code
    """

    status_code: Literal[503] = 503


class GatewayTimeoutError(ServerError):
    """HTTP 504 - Timeout from the gateway after failing to route request to destination service.

    Attributes:
        status_code: HTTP status code
    """

    status_code: Literal[504] = 504
