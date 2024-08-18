import json
from pathlib import Path

import httpx
import pytest

from openaq.shared.responses import (
    CountriesResponse,
    Country,
    Instrument,
    InstrumentsResponse,
    License,
    LicensesResponse,
    Location,
    LocationsResponse,
    Manufacturer,
    ManufacturersResponse,
    MeasurementsResponse,
    Owner,
    OwnersResponse,
    Parameter,
    ParametersResponse,
    Provider,
    ProvidersResponse,
    _ResourceBase,
    _ResponseBase,
)

RATE_LIMIT_HEADERS = {
    "X-Ratelimit-Limit": "23",
    "X-RateLimit-Used": "3",
    "X-RateLimit-Remaining": "2",
    "X-RateLimit-Reset": "60",
}


def read_resource_file(name: str) -> str:
    """Reads a JSON file from the resources direactory.

    Args:
        name: the name of the file (excluding the file extention) to be read.

    Returns:
        The body of the read file as a string.
    """
    path = Path(Path(__file__).parent, 'resources', f'{name}.json').absolute()
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def read_response_file(name: str) -> str:
    """Reads a JSON file from the responses direactory.

    Args:
        name: the name of the file (excluding the file extention) to be read.

    Returns:
        The body of the read file as a string.
    """
    path = Path(Path(__file__).parent, 'responses', f'{name}.json').absolute()
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def mock_response(data: str) -> httpx.Response:
    return httpx.Response(
        status_code=200, headers=RATE_LIMIT_HEADERS, json=json.loads(data)
    )


@pytest.mark.respx(base_url="https://api.openaq.org/v3/")
def test_rate_limit_headers_response():
    """Tests that example JSON responses validate against response models."""
    response = read_response_file('locations')
    mocked = mock_response(response)
    location = LocationsResponse.read_response(mocked)
    assert location.headers.x_ratelimit_limit == 23


@pytest.mark.parametrize(
    "name,resource_class",
    [
        ('country', Country),
        ('instrument', Instrument),
        ('license', License),
        ('location', Location),
        ('manufacturer', Manufacturer),
        ('owner', Owner),
        ('parameter', Parameter),
        ('provider', Provider),
    ],
)
@pytest.mark.respx(base_url="https://api.openaq.org/v3/")
def test_resources_validation(name: str, resource_class: _ResourceBase):
    """Tests that example JSON responses validate against response models."""
    resource = read_resource_file(name)
    resource_dict = json.loads(resource)
    try:
        resource_class.load(resource_dict)
    except Exception as e:
        pytest.fail(
            f"Model validation failed for {name}.json against {resource_class} resource model {e}"
        )


@pytest.mark.parametrize(
    "name,response_class",
    [
        ('measurements', MeasurementsResponse),
        ('countries', CountriesResponse),
        ('locations', LocationsResponse),
        ('providers', ProvidersResponse),
        ('parameters', ParametersResponse),
        ('instruments', InstrumentsResponse),
        ('owners', OwnersResponse),
        ('manufacturers', ManufacturersResponse),
        ('locations_variation', LocationsResponse),
    ],
)
@pytest.mark.respx(base_url="https://api.openaq.org/v3/")
def test_responses_validation(name: str, response_class: _ResponseBase):
    """Tests that example JSON responses validate against response models."""
    response = read_response_file(name)
    mocked = mock_response(response)
    try:
        response_class.read_response(mocked)
    except Exception as e:
        pytest.fail(
            f"Model validation failed for {name}.json against {response_class} response model {e}"
        )


@pytest.mark.parametrize(
    "name,response_class",
    [
        ('measurements', MeasurementsResponse),
        ('countries', CountriesResponse),
        ('locations', LocationsResponse),
        ('providers', ProvidersResponse),
        ('parameters', ParametersResponse),
        ('instruments', InstrumentsResponse),
        ('owners', OwnersResponse),
        ('manufacturers', ManufacturersResponse),
        ('locations_variation', LocationsResponse),
    ],
)
@pytest.mark.respx(base_url="https://api.openaq.org/v3/")
def test_responses_json(name: str, response_class: _ResponseBase):
    """Tests that example JSON responses validate against response models."""
    response = read_response_file(name)
    mocked = mock_response(response)
    d = json.loads(response_class.read_response(mocked).json())
    headers_less_response = {k: d[k] for k in set(list(d.keys())) - set(['headers'])}

    assert json.loads(response) == headers_less_response


def test_response_ignores_unexpected_fields():
    """Tests that the response model ignores unexpected fields."""
    base_response = read_response_file('locations')
    base_json = json.loads(base_response)
    modified_json = json.loads('{"anotherField": null}')
    base_json['results'][0].update(modified_json)
    mocked = mock_response(json.dumps(base_json))
    try:
        response_instance = LocationsResponse.read_response(mocked)
        assert not hasattr(
            response_instance.results[0], 'anotherField'
        ), "Unexpected 'anotherField' was not ignored"
    except Exception as e:
        pytest.fail(f"Deserialization failed with unexpected field 'anotherField': {e}")
