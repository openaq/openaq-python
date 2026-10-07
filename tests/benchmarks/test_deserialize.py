import pytest

from openaq.core import responses as r


@pytest.mark.parametrize(
    ("name", "cls", "n"),
    [
        pytest.param("measurements_1000", r.MeasurementsResponse, 1, id="measurements-1"),
        pytest.param("measurements_1000", r.MeasurementsResponse, None, id="measurements-1000"),
        pytest.param("locations_1000", r.LocationsResponse, None, id="locations"),
        pytest.param("sensors", r.SensorsResponse, None, id="sensors"),
        pytest.param("latest_1000", r.LatestResponse, None, id="latest"),
    ],
)
def test_parse(benchmark, make_response, name, cls, n):
    benchmark(cls.read_response, make_response(name, n=n))


def test_parse_with_json_decode(benchmark, make_response):
    benchmark(
        r.MeasurementsResponse.read_response,
        make_response("measurements_1000", raw=True),
    )
