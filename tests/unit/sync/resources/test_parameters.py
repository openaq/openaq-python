from unittest.mock import Mock

import pytest

from openaq._sync.models.parameters import Parameters
from openaq.shared.exceptions import (
    IdentifierOutOfBoundsError,
    InvalidParameterError,
)
from openaq.shared.responses import LatestResponse, ParametersResponse


@pytest.fixture
def mock_client():
    return Mock()


@pytest.fixture
def mock_single_response():
    response = Mock()
    response.json.return_value = {
        "meta": {
            "name": "openaq-api",
            "website": "/",
            "page": 1,
            "limit": 100,
            "found": 1,
        },
        "results": [
            {
                "id": 2,
                "name": "pm25",
                "units": "µg/m³",
                "displayName": "PM2.5",
                "description": "Particulate matter less than 2.5 micrometers in diameter mass concentration",
            },
        ],
    }
    response.headers = {}

    return response


@pytest.fixture
def mock_list_response():
    response = Mock()
    response.json.return_value = {
        "meta": {
            "name": "openaq-api",
            "website": "/",
            "page": 1,
            "limit": 100,
            "found": 2,
        },
        "results": [
            {
                "id": 1,
                "name": "pm10",
                "units": "µg/m³",
                "displayName": "PM10",
                "description": "Particulate matter less than 10 micrometers in diameter mass concentration",
            },
            {
                "id": 2,
                "name": "pm25",
                "units": "µg/m³",
                "displayName": "PM2.5",
                "description": "Particulate matter less than 2.5 micrometers in diameter mass concentration",
            },
        ],
    }
    response.headers = {}

    return response


@pytest.fixture
def mock_latest_response():
    response = Mock()
    response.json.return_value = {
        "meta": {
            "name": "openaq-api",
            "website": "/",
            "page": 1,
            "limit": 100,
            "found": 2,
        },
        "results": [
            {
                "datetime": {
                    "utc": "2025-11-26T15:00:00Z",
                    "local": "2025-11-27T00:00:00+09:00",
                },
                "value": 26,
                "coordinates": {"latitude": 35.21815, "longitude": 128.57425},
                "sensorsId": 8539597,
                "locationsId": 2622686,
            },
            {
                "datetime": {
                    "utc": "2025-11-26T14:00:00Z",
                    "local": "2025-11-26T16:00:00+02:00",
                },
                "value": -1,
                "coordinates": {
                    "latitude": 54.88361359025449,
                    "longitude": 23.83583450024486,
                },
                "sensorsId": 23735,
                "locationsId": 8152,
            },
        ],
    }
    response.headers = {}

    return response


@pytest.fixture
def parameters(mock_client):
    return Parameters(mock_client)


class TestParameters:
    def test_get_calls_client_correctly(
        self, parameters, mock_client, mock_single_response
    ):
        mock_client._get.return_value = mock_single_response
        result = parameters.get(2)
        mock_client._get.assert_called_once_with("/parameters/2")
        assert isinstance(result, ParametersResponse)
        assert len(result.results) == 1

    def test_latest_calls_client_correctly(
        self, parameters, mock_client, mock_latest_response
    ):
        mock_client._get.return_value = mock_latest_response
        result = parameters.latest(2)
        mock_client._get.assert_called_once_with("/parameters/2/latest")
        assert isinstance(result, LatestResponse)
        assert len(result.results) == 2

    def test_list_with_defaults(self, parameters, mock_client, mock_list_response):
        mock_client._get.return_value = mock_list_response
        result = parameters.list()
        params = mock_client._get.call_args[1]["params"]
        assert mock_client._get.call_args[0][0] == "/parameters"
        assert params["page"] == 1
        assert params["limit"] == 1000
        assert isinstance(result, ParametersResponse)
        assert len(result.results) == 2

    def test_list_with_pagination(self, parameters, mock_client, mock_list_response):
        mock_client._get.return_value = mock_list_response
        parameters.list(page=3, limit=50)
        params = mock_client._get.call_args[1]["params"]
        assert params["page"] == 3
        assert params["limit"] == 50

    @pytest.mark.parametrize(
        "sort_order,expected",
        [
            ("asc", "asc"),
            ("desc", "desc"),
        ],
    )
    def test_list_with_sorting(
        self, parameters, mock_client, mock_list_response, sort_order, expected
    ):
        mock_client._get.return_value = mock_list_response
        parameters.list(order_by="id", sort_order=sort_order)
        params = mock_client._get.call_args[1]["params"]
        assert params["order_by"] == "id"
        assert params["sort_order"] == expected

    @pytest.mark.parametrize(
        "value",
        [('42'), (2**31), (-1), (0)],
        ids=[
            "invalid, number as string",
            "invalid, out of int32 range",
            "invalid, negative number",
            "invalid, zero",
        ],
    )
    def test_parameters_get_throws(self, parameters, value):
        with pytest.raises(IdentifierOutOfBoundsError):
            parameters.get(value)

    @pytest.mark.parametrize(
        "value",
        [('42'), (2**31), (-1), (0)],
        ids=[
            "invalid, number as string",
            "invalid, out of int32 range",
            "invalid, negative number",
            "invalid, zero",
        ],
    )
    def test_parameters_latest_throws(self, parameters, value):
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
            ('iso', 42),
            ('iso', True),
            ('iso', 'USA'),
            ('countries_id', 2**31),
            ('countries_id', '999'),
            ('countries_id', [1, 2, 3, '4']),
            ('countries_id', [1, 2, 3, 2**31]),
            ('countries_id', True),
            ('sort_order', 'foo'),
            ('sort_order', 1),
            ('sort_order', False),
            ('order_by', 1),
            ('order_by', False),
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
            'order_by invalid value bool',
        ],
    )
    def test_parameters_list_throws(self, parameters, parameter, value):
        mock_params = {parameter: value}
        with pytest.raises(InvalidParameterError):
            parameters.list(**mock_params)
