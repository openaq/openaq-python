import http.client

import pytest

from openaq.core.exceptions import (
    BadGatewayError,
    BadRequestError,
    ForbiddenError,
    GatewayTimeoutError,
    HTTPRateLimitError,
    NotAuthorizedError,
    NotFoundError,
    ServerError,
    ServiceUnavailableError,
    TimeoutError,
    ValidationError,
)
from openaq.core.transport import Response, check_response


def make_response(status_code: int) -> Response:
    msg = http.client.HTTPMessage()
    return Response(status_code, b"", msg)


@pytest.mark.parametrize(
    "http_code,exception",
    [
        (400, BadRequestError),
        (401, NotAuthorizedError),
        (403, ForbiddenError),
        (408, TimeoutError),
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
    with pytest.raises(exception):
        check_response(make_response(http_code))


@pytest.mark.parametrize("http_code", [200, 201, 202, 204])
def test_check_response_successful(http_code):
    response = make_response(http_code)
    assert check_response(response) == response
