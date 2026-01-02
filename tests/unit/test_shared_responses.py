import json
from pathlib import Path

import httpx

from dataclasses import fields
from typing import get_type_hints, get_origin, Union, get_args
import numbers
import types

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
    Sensor,
    SensorsResponse,
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

def remove_nulls(value):
    if isinstance(value, dict):
        return {k: remove_nulls(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [remove_nulls(v) for v in value]
    else:
        return value

def value_matches_type(value, expected_type) -> bool:
    """Currently has some special cases covered(Union, numbers, lists with same 
    type values, tuples), but making this test fully generic is not trivial"""
    if expected_type is float:
        return isinstance(value, numbers.Real)

    if expected_type is int:
        return isinstance(value, numbers.Integral)

    origin = get_origin(expected_type)
    if origin is Union or origin is types.UnionType:   
        return any(value_matches_type(value, t) for t in get_args(expected_type))
    
    if origin is not None and not isinstance(value, origin):
        return False

    args = get_args(expected_type)

    if origin is list:
        if not isinstance(value, list):
            return False

        (item_type,) = args

        return all(value_matches_type(v, item_type) for v in value) 
    
    if origin is tuple and len(args) == 2 and args[1] is Ellipsis:
        return all(value_matches_type(v, args[0]) for v in value)

    if origin is tuple:
        return len(value) == len(args) and all(
            value_matches_type(v, t) for v, t in zip(value, args)
        )

    return isinstance(value, expected_type)

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
        ('sensor', Sensor),
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
        ('licenses', LicensesResponse),
        ('owners', OwnersResponse),
        ('manufacturers', ManufacturersResponse),
        ('locations_variation', LocationsResponse),
        ('sensors', SensorsResponse),
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
        ('sensors', SensorsResponse),
    ],
)
@pytest.mark.respx(base_url="https://api.openaq.org/v3/")
def test_responses_json(name: str, response_class: _ResponseBase):
    """Tests that example JSON responses validate against response models."""
    response = read_response_file(name)
    mocked = mock_response(response)
    response_data = response_class.read_response(mocked)
    d = json.loads(response_data.json())
    headers_less_response = {k: d[k] for k in set(list(d.keys())) - set(['headers'])}

    assert remove_nulls(json.loads(response)) == remove_nulls(headers_less_response)


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
        ('sensors', SensorsResponse),
    ],
)

@pytest.mark.respx(base_url="https://api.openaq.org/v3/")
def test_field_types(name: str, response_class: _ResponseBase):
    """Tests whether all fields have the correct types"""
    response = read_response_file(name)
    mocked = mock_response(response)
    response_data = response_class.read_response(mocked)

    for response_data in response_data.results:
        type_hints = get_type_hints(type(response_data))

        for field in fields(response_data):
            value = getattr(response_data, field.name)
            expected_type = type_hints.get(field.name)

            assert value_matches_type(value, expected_type)
