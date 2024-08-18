import httpx
import pytest

from openaq.shared.exceptions import (
    BadRequestError,
    Forbidden,
    GatewayTimeoutError,
    NotAuthorized,
    NotFoundError,
    RateLimit,
    ServerError,
    ValidationError,
)
from openaq.shared.transport import check_response


@pytest.mark.parametrize(
    "http_code,exception",
    [
        (400, BadRequestError),
        (422, ValidationError),
        (429, RateLimit),
        (404, NotFoundError),
        (500, ServerError),
        (504, GatewayTimeoutError),
        (401, NotAuthorized),
        (403, Forbidden),
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
