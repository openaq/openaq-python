import pytest

from openaq.core import responses as r


@pytest.fixture(
    params=[
        pytest.param(("measurements_1000", r.MeasurementsResponse), id="measurements-1000"),
        pytest.param(("locations_1000", r.LocationsResponse), id="locations-1000"),
    ]
)
def parsed(request, make_response):
    name, cls = request.param
    return cls.read_response(make_response(name))


def test_json_stdlib(benchmark, parsed):
    benchmark(parsed.json)


def test_json_orjson(benchmark, parsed):
    orjson = pytest.importorskip("orjson")
    benchmark(parsed.json, encoder=orjson)


def test_dict(benchmark, parsed):
    benchmark(parsed.dict)
