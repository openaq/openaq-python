import pytest
from openaq.core.responses import MeasurementsResponse

class FakeResponse:
    def __init__(self, body):
        self._body = body
        self.headers = {"x-ratelimit-limit": "60", "x-ratelimit-remaining": "59",
                        "x-ratelimit-used": "1", "x-ratelimit-reset": "30"}
    def json(self):
        return self._body

@pytest.fixture
def measurements_page(load_response):
    return FakeResponse(load_response("measurements_1000"))

@pytest.mark.benchmark
def test_parse_measurements(measurements_page):
    MeasurementsResponse.read_response(measurements_page)

@pytest.mark.benchmark
def test_serialize_measurements(measurements_page):
    MeasurementsResponse.read_response(measurements_page).json()
