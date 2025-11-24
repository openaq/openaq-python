from unittest.mock import MagicMock, Mock

import pytest

from openaq._sync.models.base import SyncResourceBase
from openaq._sync.models.measurements import Measurements
from openaq._sync.models.locations import Locations
from openaq._sync.models.countries import Countries
from openaq._sync.models.parameters import Parameters
from openaq._sync.models.licenses import Licenses
from openaq._sync.models.providers import Providers
from openaq.shared.exceptions import NotFoundError, InvalidParameterError, IdentifierOutOfBoundsError
from openaq.shared.responses import MeasurementsResponse, LocationsResponse, ProvidersResponse, CountriesResponse, ParametersResponse, LicensesResponse


@pytest.fixture
def mock_client():
    return Mock()


def test_sync_resource_base_init():
    mock_client = MagicMock()
    resource = SyncResourceBase(client=mock_client)
    assert resource._client == mock_client

@pytest.fixture
def countries(mock_client):
    return Countries(mock_client)

@pytest.fixture
def parameters(mock_client):
    return Parameters(mock_client)

@pytest.fixture
def providers(mock_client):
    return Providers(mock_client)

@pytest.fixture
def licenses(mock_client):
    return Parameters(mock_client)


@pytest.fixture
def measurements(mock_client):
    return Measurements(mock_client)


@pytest.fixture
def locations(mock_client):
    return Locations(mock_client)


@pytest.mark.parametrize(
    "value",
    [('42'),( 2**31), (-1),( 0)],
    ids=[
        "invalid, number as string",
        "invalid, out of int32 range",
        "invalid, negative number",
        "invalid, zero"
    ]
)
def test_parameters_get_throws(parameters, mock_client, mocker, value):
    mock_response = Mock()
    mocker.patch.object(ParametersResponse, 'read_response', return_value=mock_response)
    mock_client._get.return_value = mock_response
    with pytest.raises(IdentifierOutOfBoundsError):
        parameters.get(value)


@pytest.mark.parametrize(
    "value",
    [('42'),( 2**31), (-1),( 0)],
    ids=[
        "invalid, number as string",
        "invalid, out of int32 range",
        "invalid, negative number",
        "invalid, zero"
    ]
)
def test_countries_get_throws(countries, mock_client, mocker, value):
    mock_response = Mock()
    mocker.patch.object(CountriesResponse, 'read_response', return_value=mock_response)
    mock_client._get.return_value = mock_response
    with pytest.raises(IdentifierOutOfBoundsError):
        countries.get(value)


@pytest.mark.parametrize(
    "value",
    [('42'),( 2**31), (-1),( 0)],
    ids=[
        "invalid, number as string",
        "invalid, out of int32 range",
        "invalid, negative number",
        "invalid, zero"
    ]
)
def test_providers_get_throws(providers, mock_client, mocker, value):
    mock_response = Mock()
    mocker.patch.object(ProvidersResponse, 'read_response', return_value=mock_response)
    mock_client._get.return_value = mock_response
    with pytest.raises(IdentifierOutOfBoundsError):
        providers.get(value)

        
@pytest.mark.parametrize(
    "value",
    [('42'),( 2**31), (-1),( 0)],
    ids=[
        "invalid, number as string",
        "invalid, out of int32 range",
        "invalid, negative number",
        "invalid, zero"
    ]
)
def test_locations_get_throws(locations, mock_client, mocker, value):
    mock_response = Mock()
    mocker.patch.object(LocationsResponse, 'read_response', return_value=mock_response)
    mock_client._get.return_value = mock_response
    with pytest.raises(IdentifierOutOfBoundsError):
        locations.get(value)
        
@pytest.mark.parametrize(
    "parameter,value",
    [
        ('page', '1'),
        ('limit', '1000'),
        ('limit', 9999),
        ('providers_id', 2**31),
        ('providers_id', '999'),
        ('providers_id', [1,2,3,'4']),
        ('providers_id', [1,2,3, 2**31]),
        ('providers_id', True),
        ('countries_id', 2**31),
        ('countries_id', '999'),
        ('countries_id', [1,2,3,'4']),
        ('countries_id', [1,2,3, 2**31]),
        ('countries_id', True),
        ('parameters_id', 2**31),
        ('parameters_id', '999'),
        ('parameters_id', [1,2,3,'4']),
        ('parameters_id', [1,2,3, 2**31]),
        ('parameters_id', True),        
        ('licenses_id', 2**31),
        ('licenses_id', '999'),
        ('licenses_id', [1,2,3,'4']),
        ('licenses_id', [1,2,3, 2**31]),
        ('licenses_id', True),
        ('iso',42),
        ('iso',True),
        ('iso', 'USA')

    ],
    ids=[
        'page value invalid type',
        'limit value invalid type',
        'limit value out of range',
        'providers_id out of int range',
        'providers_id invalid type, string',
        'providers_id list contains invalid type, string',
        'providers_id list contains int out of range',
        'providers_id invalid type, boolean',
        'countries_id out of int range',
        'countries_id invalid type, string',
        'countries_id list contains invalid type, string',
        'countries_id list contains int out of range',
        'countries_id invalid type, boolean',
        'parameters_id out of int range',
        'parameters_id invalid type, string',
        'parameters_id list contains invalid type, string',
        'parameters_id list contains int out of range',
        'parameters_id invalid type, boolean',
        'parameters_id out of int range',
        'parameters_id invalid type, string',
        'parameters_id list contains invalid type, string',
        'parameters_id list contains int out of range',
        'parameters_id invalid type, boolean',
        'iso invalid type integer',
        'iso invalid type boolean',
        'iso string too many characters'
    ],
)
def test_locations_list_throws(locations, mock_client, mocker, parameter, value):
    mock_response = Mock()
    mocker.patch.object(LocationsResponse, 'read_response', return_value=mock_response)
    mock_client._get.return_value = mock_response
    mock_params = {parameter: value}
    with pytest.raises(InvalidParameterError):
        locations.list(**mock_params)


@pytest.mark.parametrize(
    "data,rollup,expected_endpoint",
    [
        (None, None, "/sensors/1/measurements"),
        ('measurements', None, "/sensors/1/measurements"),
        ('measurements', 'hourly', "/sensors/1/measurements/hourly"),
        ('hours', None, "/sensors/1/hours"),
        ('hours', 'daily', "/sensors/1/hours/daily"),
        ('days', None, "/sensors/1/days"),
        ('days', 'yearly', "/sensors/1/days/yearly"),
        ('years', None, "/sensors/1/years"),
    ],
)
def test_measurements_list_endpoints(
    measurements, mock_client, mocker, data, rollup, expected_endpoint
):
    mock_response = Mock()
    mocker.patch.object(
        MeasurementsResponse, 'read_response', return_value=mock_response
    )
    mock_client._get.return_value = mock_response
    mock_params = {'page': 1, 'limit': 1000, 'datetime_from': '2016-10-10'}
    mocker.patch('openaq.shared.models.build_query_params', return_value=mock_params)
    measurements.list(sensors_id=1, data=data, rollup=rollup)

    call_args = mock_client._get.call_args

    assert call_args[0][0] == expected_endpoint
    assert call_args[1]['params'] == {
        'page': 1,
        'limit': 1000,
        'datetime_from': '2016-10-10T00:00:00',
    }


@pytest.mark.parametrize(
    "data,rollup",
    [
        (
            'hours',
            'hourly',
        ),
        (
            'days',
            'daily',
        ),
        (
            'years',
            'yearly',
        ),
    ],
)
def test_measurements_list_endpoints_not_founds(measurements, data, rollup):
    with pytest.raises(NotFoundError):
        measurements.list(sensors_id=1, data=data, rollup=rollup)
