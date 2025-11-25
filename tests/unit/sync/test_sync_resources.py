from unittest.mock import MagicMock, Mock

import pytest

from openaq._sync.models.base import SyncResourceBase
from openaq._sync.models.measurements import Measurements
from openaq._sync.models.locations import Locations
from openaq._sync.models.countries import Countries
from openaq._sync.models.parameters import Parameters
from openaq._sync.models.licenses import Licenses
from openaq._sync.models.providers import Providers
from openaq._sync.models.instruments import Instruments
from openaq._sync.models.manufacturers import Manufacturers
from openaq._sync.models.sensors import Sensors
from openaq.shared.exceptions import NotFoundError, InvalidParameterError, IdentifierOutOfBoundsError
from openaq.shared.responses import CountriesResponse, SensorsResponse, ManufacturersResponse, InstrumentsResponse, LicensesResponse, MeasurementsResponse, LocationsResponse, ProvidersResponse, CountriesResponse, ParametersResponse, LicensesResponse


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
def instruments(mock_client):
    return Instruments(mock_client)

@pytest.fixture
def parameters(mock_client):
    return Parameters(mock_client)

@pytest.fixture
def providers(mock_client):
    return Providers(mock_client)


@pytest.fixture
def sensors(mock_client):
    return Sensors(mock_client)


@pytest.fixture
def licenses(mock_client):
    return Parameters(mock_client)

@pytest.fixture
def manufacturers(mock_client):
    return Manufacturers(mock_client)

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
def test_parameters_get_throws(parameters, value):
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
def test_parameters_latest_throws(parameters, value):
    with pytest.raises(IdentifierOutOfBoundsError):
        parameters.latest(value)
        
@pytest.mark.parametrize(
    "parameter,value",
    [
        ('page', '1'),
        ('limit', '1000'),
        ('limit', 9999),
        ('parameter_type', 'invalid'),
        ('parameter_type', 1),
        ('iso',42),
        ('iso',True),
        ('iso', 'USA'),
        ('countries_id', 2**31),
        ('countries_id', '999'),
        ('countries_id', [1,2,3,'4']),
        ('countries_id', [1,2,3, 2**31]),
        ('countries_id', True),
        ('sort_order', 'foo'),
        ('sort_order', 1),
        ('sort_order', False),
        ('order_by', 1),
        ('order_by', False)
        
    ],
    ids=[
        'page value invalid type',
        'limit value invalid type',
        'limit value out of range',
        'parameter_type invalid, not supported string',
        'parameter_type invalid type int',
        'iso invalid type integer',
        'iso invalid type boolean',
        'iso string too many characters',
        'countries_id out of int range',
        'countries_id invalid type, string',
        'countries_id list contains invalid type, string',
        'countries_id list contains int out of range',
        'countries_id invalid type, boolean',
        'sort_order invalid value, unsupported string',
        'sort_order invalid value int',
        'sort_order invalid value bool',
        'order_by invalid value int',
        'order_by invalid value bool'
    ],
)
def test_parameters_list_throws(parameters, parameter, value):
    mock_params = {parameter: value}
    with pytest.raises(InvalidParameterError):
        parameters.list(**mock_params)

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
def test_licenses_get_throws(licenses, value):
    with pytest.raises(IdentifierOutOfBoundsError):
        licenses.get(value)


@pytest.mark.parametrize(
    "parameter,value",
    [
        ('page', '1'),
        ('limit', '1000'),
        ('limit', 9999),
        ('sort_order', 'foo'),
        ('sort_order', 1),
        ('sort_order', False),
        ('order_by', 1),
        ('order_by', False)
        
    ],
    ids=[
        'page value invalid type',
        'limit value invalid type',
        'limit value out of range',
        'sort_order invalid value, unsupported string',
        'sort_order invalid value int',
        'sort_order invalid value bool',
        'order_by invalid value int',
        'order_by invalid value bool'
    ],
)
def test_licenses_list_throws(licenses, parameter, value):
    mock_params = {parameter: value}
    with pytest.raises(InvalidParameterError):
        licenses.list(**mock_params)

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

def test_instruments_get_throws(instruments, value):
    with pytest.raises(IdentifierOutOfBoundsError):
        instruments.get(value)


@pytest.mark.parametrize(
    "parameter,value",
    [
        ('page', '1'),
        ('limit', '1000'),
        ('limit', 9999),
        ('sort_order', 'foo'),
        ('sort_order', 1),
        ('sort_order', False),
        ('order_by', 1),
        ('order_by', False)
        
    ],
    ids=[
        'page value invalid type',
        'limit value invalid type',
        'limit value out of range',
        'sort_order invalid value, unsupported string',
        'sort_order invalid value int',
        'sort_order invalid value bool',
        'order_by invalid value int',
        'order_by invalid value bool'
    ],
)
def test_instruments_list_throws(instruments, parameter, value):
    mock_params = {parameter: value}
    with pytest.raises(InvalidParameterError):
        instruments.list(**mock_params)


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
def test_sensors_get_throws(sensors, value):
    with pytest.raises(IdentifierOutOfBoundsError):
        sensors.get(value)
        
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


def test_manufacturers_get_throws(manufacturers, value):
    with pytest.raises(IdentifierOutOfBoundsError):
        manufacturers.get(value)

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
def test_manufacturers_instruments_throws(manufacturers, value):
    with pytest.raises(IdentifierOutOfBoundsError):
        manufacturers.instruments(value)

@pytest.mark.parametrize(
    "parameter,value",
    [
        ('page', '1'),
        ('limit', '1000'),
        ('limit', 9999),
        ('sort_order', 'foo'),
        ('sort_order', 1),
        ('sort_order', False),
        ('order_by', 1),
        ('order_by', False)
        
    ],
    ids=[
        'page value invalid type',
        'limit value invalid type',
        'limit value out of range',
        'sort_order invalid value, unsupported string',
        'sort_order invalid value int',
        'sort_order invalid value bool',
        'order_by invalid value int',
        'order_by invalid value bool'
    ],
)
def test_manufacturers_list_throws(manufacturers, parameter, value):
    mock_params = {parameter: value}
    with pytest.raises(InvalidParameterError):
        manufacturers.list(**mock_params)

        
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
def test_countries_get_throws(countries, value):
    with pytest.raises(IdentifierOutOfBoundsError):
        countries.get(value)


@pytest.mark.parametrize(
    "parameter,value",
    [
        ('page', '1'),
        ('limit', '1000'),
        ('limit', 9999),
        ('parameters_id', 2**31),
        ('parameters_id', '999'),
        ('parameters_id', [1,2,3,'4']),
        ('parameters_id', [1,2,3, 2**31]),
        ('parameters_id', True),
        ('providers_id', 2**31),
        ('providers_id', '999'),
        ('providers_id', [1,2,3,'4']),
        ('providers_id', [1,2,3, 2**31]),
        ('providers_id', True),
        ('sort_order', 'foo'),
        ('sort_order', 1),
        ('sort_order', False),
        ('order_by', 1),
        ('order_by', False)
        
    ],
    ids=[
        'page value invalid type',
        'limit value invalid type',
        'limit value out of range',
        'parameters_id out of int range',
        'parameters_id invalid type, string',
        'parameters_id list contains invalid type, string',
        'parameters_id list contains int out of range',
        'parameters_id invalid type, boolean',
        'providers_id out of int range',
        'providers_id invalid type, string',
        'providers_id list contains invalid type, string',
        'providers_id list contains int out of range',
        'providers_id invalid type, boolean',
        'sort_order invalid value, unsupported string',
        'sort_order invalid value int',
        'sort_order invalid value bool',
        'order_by invalid value int',
        'order_by invalid value bool'
    ],
)
def test_countries_list_throws(countries, parameter, value):
    mock_params = {parameter: value}
    with pytest.raises(InvalidParameterError):
        countries.list(**mock_params)

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
def test_providers_get_throws(providers, value):
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
def test_location_sensors_throws(locations, value):
    with pytest.raises(IdentifierOutOfBoundsError):
        locations.sensors(value)
        
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
def test_location_latest_throws(locations, value):
    with pytest.raises(IdentifierOutOfBoundsError):
        locations.latest(value)
        
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
def test_locations_get_throws(locations, value):
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
        ('iso', 'USA'),
        ('mobile', 'True'),
        ('mobile', 1),
        ('monitor', 'True'),
        ('monitor', 1),
        ('sort_order', 'foo'),
        ('sort_order', 1),
        ('sort_order', False),
        ('order_by', 1),
        ('order_by', False)
        
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
        'iso string too many characters',
        'mobile invalid value string',
        'mobile invalid value int',
        'monitor invalue value string',
        'monitor invalid value int',
        'sort_order invalid value, unsupported string',
        'sort_order invalid value int',
        'sort_order invalid value bool',
        'order_by invalid value int',
        'order_by invalid value bool'
    ],
)
def test_locations_list_throws(locations, parameter, value):
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
