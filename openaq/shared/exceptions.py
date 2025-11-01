"""Custom exceptions to catch various HTTP codes returned by the OpenAQ API."""

from typing import Literal


class OpenAQError(Exception):
    """Base exception for OpenAQ SDK."""

    pass


class ClientValidationError(OpenAQError):
    """Raised when input validation fails before making a request."""

    pass


class IdentifierOutOfBoundsError(ClientValidationError):
    """Raised when id field is outside valid range [1, 2_147_483_647]."""

    pass


class InvalidQueryParameterError(ClientValidationError):
    """Raised when query parameter is invalid."""

    pass


class APIError(Exception):
    """Base class for all API exceptions."""

    pass


class HTTPClientError(APIError):
    """Base class for all HTTP client exceptions HTTP 4xx."""

    pass


class ApiKeyMissingError(OpenAQError):
    """API Key missing error."""

    pass


class BadRequestError(HTTPClientError):
    """HTTP 400 - Client request error.

    Attributes:
        status_code: HTTP status code
    """

    status_code: int = 400


class NotAuthorizedError(HTTPClientError):
    """HTTP 401- Not authorized.

    Attributes:
        status_code: HTTP status code
    """

    status_code: Literal[401] = 401


class ForbiddenError(HTTPClientError):
    """HTTP 403 - Forbidden.

    Attributes:
        status_code: HTTP status code
    """

    status_code: Literal[403] = 403


class NotFoundError(HTTPClientError):
    """HTTP 404 - Resource not found.

    Attributes:
        status_code: HTTP status code
    """

    status_code: Literal[404] = 404


class TimeoutError(HTTPClientError):
    """HTTP 408 - Request Timeout.

    Attributes:
        status_code: HTTP status code
    """

    status_code: Literal[408] = 408


class ValidationError(HTTPClientError):
    """HTTP 422 - Client request with invalid parameters.

    Attributes:
        status_code: HTTP status code
    """

    status_code: Literal[422] = 422


class RateLimitError(OpenAQError):
    """Exception for catching rate limit exceedances from client."""


class HTTPRateLimitError(HTTPClientError):
    """HTTP 429 - Client request exceeds rate limits.

    Attributes:
        status_code: HTTP status code
    """

    status_code: Literal[429] = 429


class ServerError(APIError):
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
