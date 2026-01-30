from unittest.mock import AsyncMock, Mock

import pytest

from openaq._async.models.locations import Locations
from openaq.shared.exceptions import (
    IdentifierOutOfBoundsError,
    InvalidParameterError,
)
from openaq.shared.responses import (
    LatestResponse,
    LocationsResponse,
    SensorsResponse,
)


@pytest.fixture
def mock_client():
    return AsyncMock()


@pytest.fixture
def mock_sensors_response():
    response = Mock()
    response.json.return_value = {
        "meta": {
            "name": "openaq-api",
            "website": "/",
            "page": 1,
            "limit": 100,
            "found": 8,
        },
        "results": [
            {
                "id": 3920,
                "name": "pm25 µg/m³",
                "parameter": {
                    "id": 2,
                    "name": "pm25",
                    "units": "µg/m³",
                    "displayName": "PM2.5",
                },
                "datetimeFirst": {
                    "utc": "2016-03-06T20:00:00Z",
                    "local": "2016-03-06T13:00:00-07:00",
                },
                "datetimeLast": {
                    "utc": "2025-11-26T17:00:00Z",
                    "local": "2025-11-26T10:00:00-07:00",
                },
                "coverage": {
                    "expectedCount": 1,
                    "expectedInterval": "01:00:00",
                    "observedCount": 66563,
                    "observedInterval": "66563:00:00",
                    "percentComplete": 6656300,
                    "percentCoverage": 6656300,
                    "datetimeFrom": {
                        "utc": "2016-03-06T20:00:00Z",
                        "local": "2016-03-06T13:00:00-07:00",
                    },
                    "datetimeTo": {
                        "utc": "2025-11-26T17:00:00Z",
                        "local": "2025-11-26T10:00:00-07:00",
                    },
                },
                "latest": {
                    "datetime": {
                        "utc": "2025-11-26T17:00:00Z",
                        "local": "2025-11-26T10:00:00-07:00",
                    },
                    "value": 3.6,
                    "coordinates": {"latitude": 35.1353, "longitude": -106.584702},
                },
                "summary": {
                    "min": -4.9,
                    "q02": None,
                    "q25": None,
                    "median": None,
                    "q75": None,
                    "q98": None,
                    "max": 169.9,
                    "avg": 5.779898468115439,
                    "sd": None,
                },
            }
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
            "found": 8,
        },
        "results": [
            {
                "datetime": {
                    "utc": "2025-11-26T17:00:00Z",
                    "local": "2025-11-26T10:00:00-07:00",
                },
                "value": 0.013,
                "coordinates": {"latitude": 35.1353, "longitude": -106.584702},
                "sensorsId": 3916,
                "locationsId": 2178,
            },
            {
                "datetime": {
                    "utc": "2025-11-26T17:00:00Z",
                    "local": "2025-11-26T10:00:00-07:00",
                },
                "value": 0.0003,
                "coordinates": {"latitude": 35.1353, "longitude": -106.584702},
                "sensorsId": 3918,
                "locationsId": 2178,
            },
            {
                "datetime": {
                    "utc": "2025-11-26T17:00:00Z",
                    "local": "2025-11-26T10:00:00-07:00",
                },
                "value": 3.6,
                "coordinates": {"latitude": 35.1353, "longitude": -106.584702},
                "sensorsId": 3920,
                "locationsId": 2178,
            },
            {
                "datetime": {
                    "utc": "2025-11-26T17:00:00Z",
                    "local": "2025-11-26T10:00:00-07:00",
                },
                "value": 0.023,
                "coordinates": {"latitude": 35.1353, "longitude": -106.584702},
                "sensorsId": 3917,
                "locationsId": 2178,
            },
            {
                "datetime": {
                    "utc": "2025-11-26T17:00:00Z",
                    "local": "2025-11-26T10:00:00-07:00",
                },
                "value": 10,
                "coordinates": {"latitude": 35.1353, "longitude": -106.584702},
                "sensorsId": 3919,
                "locationsId": 2178,
            },
            {
                "datetime": {
                    "utc": "2025-11-26T17:00:00Z",
                    "local": "2025-11-26T10:00:00-07:00",
                },
                "value": 0.1,
                "coordinates": {"latitude": 35.1353, "longitude": -106.584702},
                "sensorsId": 25227,
                "locationsId": 2178,
            },
            {
                "datetime": {
                    "utc": "2025-09-19T16:00:00Z",
                    "local": "2025-09-19T10:00:00-06:00",
                },
                "value": 0.01,
                "coordinates": {"latitude": 35.1353, "longitude": -106.584702},
                "sensorsId": 4272103,
                "locationsId": 2178,
            },
            {
                "datetime": {
                    "utc": "2025-09-19T16:00:00Z",
                    "local": "2025-09-19T10:00:00-06:00",
                },
                "value": 0.002,
                "coordinates": {"latitude": 35.1353, "longitude": -106.584702},
                "sensorsId": 4272226,
                "locationsId": 2178,
            },
        ],
    }
    response.headers = {}
    return response


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
                "id": 2178,
                "name": "Del Norte",
                "locality": "Albuquerque",
                "timezone": "America/Denver",
                "country": {"id": 155, "code": "US", "name": "United States"},
                "owner": {"id": 4, "name": "Unknown Governmental Organization"},
                "provider": {"id": 119, "name": "AirNow"},
                "isMobile": False,
                "isMonitor": True,
                "instruments": [{"id": 2, "name": "Government Monitor"}],
                "sensors": [
                    {
                        "id": 25227,
                        "name": "co ppm",
                        "parameter": {
                            "id": 8,
                            "name": "co",
                            "units": "ppm",
                            "displayName": "CO",
                        },
                    }
                ],
                "coordinates": {"latitude": 35.1353, "longitude": -106.584702},
                "licenses": [
                    {
                        "id": 33,
                        "name": "US Public Domain",
                        "attribution": {
                            "name": "Unknown Governmental Organization",
                            "url": None,
                        },
                        "dateFrom": "2016-01-30",
                        "dateTo": None,
                    }
                ],
                "bounds": [-106.584702, 35.1353, -106.584702, 35.1353],
                "distance": None,
                "datetimeFirst": {
                    "utc": "2016-03-06T20:00:00Z",
                    "local": "2016-03-06T13:00:00-07:00",
                },
                "datetimeLast": {
                    "utc": "2025-11-26T13:00:00Z",
                    "local": "2025-11-26T06:00:00-07:00",
                },
            }
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
            "limit": 1000,
            "found": 1,
        },
        "results": [
            {
                "id": 2178,
                "name": "Del Norte",
                "locality": "Albuquerque",
                "timezone": "America/Denver",
                "country": {"id": 155, "code": "US", "name": "United States"},
                "owner": {"id": 4, "name": "Unknown Governmental Organization"},
                "provider": {"id": 119, "name": "AirNow"},
                "isMobile": False,
                "isMonitor": True,
                "instruments": [{"id": 2, "name": "Government Monitor"}],
                "sensors": [
                    {
                        "id": 25227,
                        "name": "co ppm",
                        "parameter": {
                            "id": 8,
                            "name": "co",
                            "units": "ppm",
                            "displayName": "CO",
                        },
                    }
                ],
                "coordinates": {"latitude": 35.1353, "longitude": -106.584702},
                "licenses": [
                    {
                        "id": 33,
                        "name": "US Public Domain",
                        "attribution": {
                            "name": "Unknown Governmental Organization",
                            "url": None,
                        },
                        "dateFrom": "2016-01-30",
                        "dateTo": None,
                    }
                ],
                "bounds": [-106.584702, 35.1353, -106.584702, 35.1353],
                "distance": None,
                "datetimeFirst": {
                    "utc": "2016-03-06T20:00:00Z",
                    "local": "2016-03-06T13:00:00-07:00",
                },
                "datetimeLast": {
                    "utc": "2025-11-26T13:00:00Z",
                    "local": "2025-11-26T06:00:00-07:00",
                },
            }
        ],
    }
    response.headers = {}

    return response


@pytest.fixture
def locations(mock_client):
    return Locations(mock_client)


@pytest.mark.asyncio
class TestLocations:
    async def test_get_calls_client_correctly(
        self, locations, mock_client, mock_single_response
    ):
        mock_client._get.return_value = mock_single_response
        result = await locations.get(2178)
        mock_client._get.assert_called_once_with("/locations/2178")
        assert isinstance(result, LocationsResponse)
        assert len(result.results) == 1

    async def test_latest_calls_client_correctly(
        self, locations, mock_client, mock_latest_response
    ):
        mock_client._get.return_value = mock_latest_response
        result = await locations.latest(2178)
        mock_client._get.assert_called_once_with("/locations/2178/latest")
        assert isinstance(result, LatestResponse)
        assert len(result.results) == 8

    async def test_sensors_calls_client_correctly(
        self, locations, mock_client, mock_sensors_response
    ):
        mock_client._get.return_value = mock_sensors_response
        result = await locations.sensors(2178)
        mock_client._get.assert_called_once_with("/locations/2178/sensors")
        assert isinstance(result, SensorsResponse)
        assert len(result.results) == 1

    async def test_list_with_defaults(self, locations, mock_client, mock_list_response):
        mock_client._get.return_value = mock_list_response
        result = await locations.list()
        params = mock_client._get.call_args[1]["params"]
        assert mock_client._get.call_args[0][0] == "/locations"
        assert params["page"] == 1
        assert params["limit"] == 100
        assert isinstance(result, LocationsResponse)
        assert len(result.results) == 1

    async def test_list_with_pagination(
        self, locations, mock_client, mock_list_response
    ):
        mock_client._get.return_value = mock_list_response
        await locations.list(page=3, limit=50)
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
    async def test_list_with_sorting(
        self, locations, mock_client, mock_list_response, sort_order, expected
    ):
        mock_client._get.return_value = mock_list_response
        await locations.list(order_by="id", sort_order=sort_order)
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
    async def test_location_sensors_throws(self, locations, value):
        with pytest.raises(IdentifierOutOfBoundsError):
            await locations.sensors(value)

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
    async def test_location_latest_throws(self, locations, value):
        with pytest.raises(IdentifierOutOfBoundsError):
            await locations.latest(value)

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
    async def test_locations_get_throws(self, locations, value):
        with pytest.raises(IdentifierOutOfBoundsError):
            await locations.get(value)

    @pytest.mark.parametrize(
        "parameter,value",
        [
            ('page', '1'),
            ('limit', '1000'),
            ('limit', 9999),
            ('providers_id', 2**31),
            ('providers_id', '999'),
            ('providers_id', [1, 2, 3, '4']),
            ('providers_id', [1, 2, 3, 2**31]),
            ('providers_id', True),
            ('countries_id', 2**31),
            ('countries_id', '999'),
            ('countries_id', [1, 2, 3, '4']),
            ('countries_id', [1, 2, 3, 2**31]),
            ('countries_id', True),
            ('parameters_id', 2**31),
            ('parameters_id', '999'),
            ('parameters_id', [1, 2, 3, '4']),
            ('parameters_id', [1, 2, 3, 2**31]),
            ('parameters_id', True),
            ('licenses_id', 2**31),
            ('licenses_id', '999'),
            ('licenses_id', [1, 2, 3, '4']),
            ('licenses_id', [1, 2, 3, 2**31]),
            ('licenses_id', True),
            ('iso', 42),
            ('iso', True),
            ('iso', 'USA'),
            ('mobile', 'True'),
            ('mobile', 1),
            ('monitor', 'True'),
            ('monitor', 1),
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
            'order_by invalid value bool',
        ],
    )
    async def test_locations_list_throws(self, locations, parameter, value):
        mock_params = {parameter: value}
        with pytest.raises(InvalidParameterError):
            await locations.list(**mock_params)
