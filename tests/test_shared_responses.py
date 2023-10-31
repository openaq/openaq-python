import json
from pathlib import Path

import pytest

from openaq.shared.responses import (
    CountriesResponse,
    InstrumentsResponse,
    LocationsResponse,
    ManufacturersResponse,
    MeasurementsResponse,
    OwnersResponse,
    ParametersResponse,
    ProvidersResponse,
    _ResponseBase,
)


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
    try:
        response_class.load(json.loads(response))
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
    assert json.loads(response) == json.loads(
        response_class.load(json.loads(response)).json()
    )
