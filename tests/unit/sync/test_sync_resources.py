from unittest.mock import MagicMock, Mock

import pytest

from openaq._sync.models.base import SyncResourceBase
from openaq._sync.models.measurements import Measurements
from openaq.shared.exceptions import NotFoundError
from openaq.shared.responses import MeasurementsResponse


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
    assert call_args[1]['params'] == mock_params


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
