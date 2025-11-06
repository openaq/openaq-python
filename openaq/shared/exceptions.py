"""Custom exceptions to catch various errors."""

from typing import Literal


class OpenAQError(Exception):
    """Base exception for all OpenAQ SDK errors.

    This is the root exception class for the OpenAQ SDK. All custom client-related
    exceptions in the SDK inherit from this class, allowing users to catch all
    SDK-specific client errors.

    Args:
        message (str, optional): Human readable string describing the exception.

    Example:
        try:
            client.get_locations()
        except OpenAQError as e:
            print(f"OpenAQ SDK error: {e}")
    """

    pass


class ClientValidationError(OpenAQError, ValueError):
    """Raised when input validation fails before making an API request.

    This exception is raised when user-provided parameters fail validation
    on the client side, before any HTTP request is sent to the API. Inherits
    from both OpenAQError and ValueError, allowing it to be caught as either
    an SDK-specific error or a standard Python value error.

    Args:
        message (str, optional): Human readable string describing the validation
        error.

    Example:
        try:
            client.get_location(location_id=-1)
        except ClientValidationError as e:
            print(f"Invalid parameter: {e}")
        except ValueError as e:
            print(f"Value error: {e}")
    """

    pass


class IdentifierOutOfBoundsError(ClientValidationError):
    """Raised when an ID field is outside the valid range [1, 2_147_483_647].

    This exception is raised when a user provides an identifier (such as a
    location_id, parameter_id, etc.) that falls outside the acceptable range
    defined by the API constraints.

    Args:
        message (str, optional): Human readable string describing which identifier
        is out of bounds.

    Example:
        try:
            client.get_location(location_id=3_000_000_000)
        except IdentifierOutOfBoundsError as e:
            print(f"ID out of bounds: {e}")
    """

    pass


class InvalidParameterError(ClientValidationError):
    """Raised when a query parameter value is invalid.

    This exception is raised when a parameter value doesn't meet the API's
    requirements (e.g., invalid enum value, malformed string, incorrect type).

    Args:
        message (str, optional): Human readable string describing which parameter
            is invalid and why.

    Example:
        try:
            client.get_locations(limit=-10)
        except InvalidParameterError as e:
            print(f"Invalid parameter: {e}")
    """

    pass


class APIError(Exception):
    """Base class for all API-related exceptions.

    This is the parent class for exceptions that occur due to API responses,
    including both client errors (4xx) and server errors (5xx).

    Args:
        message (str, optional): Human readable string describing the API error.

    Note:
        This is separate from OpenAQError to distinguish between client-side
        validation errors and actual API response errors.
    """

    pass


class HTTPClientError(APIError):
    """Base class for all HTTP 4xx client error responses.

    Raised when the API returns a 4xx status code, indicating that the request
    was malformed, unauthorized, or otherwise invalid from the client's side.

    Args:
        message (str, optional): Human readable string describing the client error.

    Attributes:
        status_code (int): The HTTP status code returned by the API.
    """

    pass


class ApiKeyMissingError(OpenAQError):
    """Raised when an API key is required but not provided.

    This exception is raised when attempting to access endpoints that require
    authentication but no API key has been configured in the client.

    Args:
        message (str, optional): Human readable string describing the missing
            API key requirement.

    Example:
        try:
            client = OpenAQ()  # No API key provided
            client.get_protected_resource()
        except ApiKeyMissingError as e:
            print(f"API key required: {e}")
    """

    pass


class BadRequestError(HTTPClientError):
    """HTTP 400 - Bad Request.

    Raised when the API returns a 400 status code, indicating that the request
    was malformed or contains invalid syntax.

    Args:
        message (str, optional): Human readable string describing the bad request.

    Attributes:
        status_code (int): HTTP status code (400).

    Example:
        try:
            client.get_locations(invalid_param="bad_value")
        except BadRequestError as e:
            print(f"Bad request: {e}")
    """

    status_code: int = 400


class NotAuthorizedError(HTTPClientError):
    """HTTP 401 - Unauthorized.

    Raised when the API returns a 401 status code, indicating that authentication
    is required or the provided credentials are invalid.

    Args:
        message (str, optional): Human readable string describing the authorization
            failure.

    Attributes:
        status_code (int): HTTP status code (401).

    Example:
        try:
            client = OpenAQ(api_key="invalid_key")
            client.get_measurements()
        except NotAuthorizedError as e:
            print(f"Authentication failed: {e}")
    """

    status_code: Literal[401] = 401


class ForbiddenError(HTTPClientError):
    """HTTP 403 - Forbidden.

    Raised when the API returns a 403 status code, indicating that the client
    is authenticated but does not have permission to access the requested resource.

    Args:
        message (str, optional): Human readable string describing why access
            was forbidden.

    Attributes:
        status_code (int): HTTP status code (403).

    Example:
        try:
            client.delete_resource(resource_id=123)
        except ForbiddenError as e:
            print(f"Access denied: {e}")
    """

    status_code: Literal[403] = 403


class NotFoundError(HTTPClientError):
    """HTTP 404 - Not Found.

    Raised when the API returns a 404 status code, indicating that the requested
    resource does not exist.

    Args:
        message (str, optional): Human readable string describing which resource
            was not found.

    Attributes:
        status_code (int): HTTP status code (404).

    Example:
        try:
            client.get_location(location_id=999999)
        except NotFoundError as e:
            print(f"Resource not found: {e}")
    """

    status_code: Literal[404] = 404


class TimeoutError(HTTPClientError):
    """HTTP 408 - Request Timeout.

    Raised when the API returns a 408 status code, indicating that the server
    timed out waiting for the request to complete.

    Args:
        message (str, optional): Human readable string describing the timeout.

    Attributes:
        status_code (int): HTTP status code (408).

    Note:
        This is different from network-level timeouts, which may raise different
        exceptions depending on the HTTP client library used.

    Example:
        try:
            client.get_measurements(date_from="2000-01-01", date_to="2024-12-31")
        except TimeoutError as e:
            print(f"Request timed out: {e}")
    """

    status_code: Literal[408] = 408


class ValidationError(HTTPClientError):
    """HTTP 422 - Unprocessable Entity.

    Raised when the API returns a 422 status code, indicating that the request
    was well-formed but contains semantic errors or invalid parameter combinations.

    Args:
        message (str, optional): Human readable string describing the validation
            error.

    Attributes:
        status_code (int): HTTP status code (422).

    Example:
        try:
            client.get_measurements(date_from="2024-01-01", date_to="2023-01-01")
        except ValidationError as e:
            print(f"Validation error: {e}")
    """

    status_code: Literal[422] = 422


class RateLimitError(OpenAQError):
    """Raised when client-side rate limiting is triggered.

    This exception is raised by the SDK's internal rate limiting mechanism
    before making a request that would exceed configured rate limits. This is
    separate from HTTPRateLimitError, which indicates server-side rate limiting.

    Args:
        message (str, optional): Human readable string describing the rate limit
            that was exceeded.

    Example:
        try:
            for i in range(1000):
                client.get_locations()
        except RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
    """

    pass


class HTTPRateLimitError(HTTPClientError):
    """HTTP 429 - Too Many Requests.

    Raised when the API returns a 429 status code, indicating that the client
    has exceeded the server-side rate limits.

    Args:
        message (str, optional): Human readable string describing the rate limit
            error.

    Attributes:
        status_code (int): HTTP status code (429).

    Example:
        try:
            for i in range(10000):
                client.get_locations()
        except HTTPRateLimitError as e:
            print(f"API rate limit exceeded: {e}")
    """

    status_code: Literal[429] = 429


class ServerError(APIError):
    """HTTP 5xx - Server Error.

    Base class for all HTTP 5xx server error responses. Raised when the API
    encounters an internal error or is unable to process the request due to
    server-side issues.

    Args:
        message (str, optional): Human readable string describing the server error.

    Attributes:
        status_code (int): HTTP status code (500 or specific 5xx code).

    Example:
        try:
            client.get_locations()
        except ServerError as e:
            print(f"Server error: {e}")
    """

    status_code: int = 500


class BadGatewayError(ServerError):
    """HTTP 502 - Bad Gateway.

    Raised when the API returns a 502 status code, indicating that the gateway
    or proxy received an invalid response from an upstream server.

    Args:
        message (str, optional): Human readable string describing the bad gateway
            error.

    Attributes:
        status_code (int): HTTP status code (502).

    Example:
        try:
            client.get_measurements()
        except BadGatewayError as e:
            print(f"Bad gateway: {e}")
    """

    status_code: Literal[502] = 502


class ServiceUnavailableError(ServerError):
    """HTTP 503 - Service Unavailable.

    Raised when the API returns a 503 status code, indicating that the server
    is temporarily unable to handle the request, typically due to maintenance
    or overload.

    Args:
        message (str, optional): Human readable string describing why the service
            is unavailable.

    Attributes:
        status_code (int): HTTP status code (503).

    Example:
        try:
            client.get_locations()
        except ServiceUnavailableError as e:
            print(f"Service unavailable, try again later: {e}")
    """

    status_code: Literal[503] = 503


class GatewayTimeoutError(ServerError):
    """HTTP 504 - Gateway Timeout.

    Raised when the API returns a 504 status code, indicating that the gateway
    or proxy timed out while waiting for a response from an upstream server.

    Args:
        message (str, optional): Human readable string describing the gateway
            timeout.

    Attributes:
        status_code (int): HTTP status code (504).

    Example:
        try:
            client.get_measurements()
        except GatewayTimeoutError as e:
            print(f"Gateway timeout: {e}")
    """

    status_code: Literal[504] = 504
