from unittest.mock import MagicMock, Mock

import pytest

from openaq._sync.models.base import SyncResourceBase
from openaq._sync.models.measurements import Measurements
from openaq._sync.models.locations import Locations
from openaq.shared.exceptions import NotFoundError, InvalidParameterError
from openaq.shared.responses import MeasurementsResponse, LocationsResponse

@pytest.fixture
def mock_client():
    return Mock()


def test_sync_resource_base_init():
    mock_client = MagicMock()
    resource = SyncResourceBase(client=mock_client)
    assert resource._client == mock_client


@pytest.fixture
def measurements(mock_client):
    return Measurements(mock_client)

@pytest.fixture
def locations(mock_client):
    return Locations(mock_client)

@pytest.mark.parametrize(
    "parameter,value,description",
    [
        ('page', '1','page value invalid type'),
        ('limit','1000', 'limit value invalid type'),
        ('limit', 9999, 'limit value out of range'),
    ]
)
def test_locations_list_throws(
    locations, mock_client, mocker,parameter, value, description
):
    mock_response = Mock()
    LocationsResponse.read_response = Mock(return_value=mock_response)
    mock_client._get.return_value = mock_response
    mock_params = {parmater: value}  
    mocker.patch('openaq.shared.models.build_query_params', return_value=mock_params)
    with pytest.raises(InvalidParameterError):
        locations.list(sensors_id=1, data=data, rollup=rollup)



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
    MeasurementsResponse.read_response = Mock(return_value=mock_response)
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


