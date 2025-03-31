import httpx
import pytest

from openaq.shared.exceptions import (
    BadGatewayError,
    BadRequestError,
    ForbiddenError,
    GatewayTimeoutError,
    HTTPRateLimitError,
    NotAuthorizedError,
    NotFoundError,
    ServerError,
    ServiceUnavailableError,
    ValidationError,
)
from openaq.shared.transport import check_response


@pytest.mark.parametrize(
    "http_code,exception",
    [
        (400, BadRequestError),
        (401, NotAuthorizedError),
        (403, ForbiddenError),
        (404, NotFoundError),
        (418, Exception),
        (422, ValidationError),
        (429, HTTPRateLimitError),
        (500, ServerError),
        (502, BadGatewayError),
        (503, ServiceUnavailableError),
        (504, GatewayTimeoutError),
    ],
)
def test_check_response(http_code, exception):
    response = httpx.Response(http_code)
    with pytest.raises(exception):
        check_response(response)


@pytest.mark.parametrize("http_code", [200, 201, 202, 204])
def test_check_response_successful(http_code):
    response = httpx.Response(http_code)
    assert check_response(response) == response
