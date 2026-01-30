from unittest.mock import AsyncMock, Mock

import pytest

from openaq._async.models.providers import Providers
from openaq.shared.exceptions import (
    IdentifierOutOfBoundsError,
    InvalidParameterError,
)
from openaq.shared.responses import ProvidersResponse


@pytest.fixture
def mock_client():
    return AsyncMock()


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
                "id": 119,
                "name": "AirNow",
                "sourceName": "AirNow",
                "exportPrefix": "airnow",
                "datetimeAdded": "2023-03-29T20:23:57.054584Z",
                "datetimeFirst": "2016-01-30T02:00:00Z",
                "datetimeLast": "2025-11-26T15:15:00Z",
                "entitiesId": 1,
                "parameters": [
                    {"id": 1, "name": "pm10", "units": "µg/m³", "displayName": None},
                    {"id": 2, "name": "pm25", "units": "µg/m³", "displayName": None},
                ],
                "bbox": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-161.767, -34.5766],
                            [-161.767, 70.1319],
                            [123.424434, 70.1319],
                            [123.424434, -34.5766],
                            [-161.767, -34.5766],
                        ]
                    ],
                },
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
            "found": 1,
        },
        "results": [
            {
                "id": 119,
                "name": "AirNow",
                "sourceName": "AirNow",
                "exportPrefix": "airnow",
                "datetimeAdded": "2023-03-29T20:23:57.054584Z",
                "datetimeFirst": "2016-01-30T02:00:00Z",
                "datetimeLast": "2025-11-26T15:15:00Z",
                "entitiesId": 1,
                "parameters": [
                    {"id": 1, "name": "pm10", "units": "µg/m³", "displayName": None},
                    {"id": 2, "name": "pm25", "units": "µg/m³", "displayName": None},
                ],
                "bbox": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-161.767, -34.5766],
                            [-161.767, 70.1319],
                            [123.424434, 70.1319],
                            [123.424434, -34.5766],
                            [-161.767, -34.5766],
                        ]
                    ],
                },
            },
        ],
    }
    response.headers = {}

    return response


@pytest.fixture
def providers(mock_client):
    return Providers(mock_client)


@pytest.mark.asyncio
class TestProviders:
    async def test_get_calls_client_correctly(
        self, providers, mock_client, mock_single_response
    ):
        mock_client._get.return_value = mock_single_response
        result = await providers.get(119)
        mock_client._get.assert_called_once_with("/providers/119")
        assert isinstance(result, ProvidersResponse)
        assert len(result.results) == 1

    async def test_list_with_defaults(self, providers, mock_client, mock_list_response):
        mock_client._get.return_value = mock_list_response
        result = await providers.list()
        params = mock_client._get.call_args[1]["params"]
        assert mock_client._get.call_args[0][0] == "/providers"
        assert params["page"] == 1
        assert params["limit"] == 1000
        assert isinstance(result, ProvidersResponse)
        assert len(result.results) == 1

    async def test_list_with_pagination(
        self, providers, mock_client, mock_list_response
    ):
        mock_client._get.return_value = mock_list_response
        await providers.list(page=3, limit=50)
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
        self, providers, mock_client, mock_list_response, sort_order, expected
    ):
        mock_client._get.return_value = mock_list_response
        await providers.list(order_by="id", sort_order=sort_order)
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
    async def test_providers_get_throws(self, providers, value):
        with pytest.raises(IdentifierOutOfBoundsError):
            await providers.get(value)

    @pytest.mark.parametrize(
        "parameter,value",
        [
            ('page', '1'),
            ('limit', '1000'),
            ('limit', 9999),
            ('iso', 42),
            ('iso', True),
            ('iso', 'USA'),
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
            'iso invalid type integer',
            'iso invalid type boolean',
            'iso string too many characters',
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
            'sort_order invalid value, unsupported string',
            'sort_order invalid value int',
            'sort_order invalid value bool',
            'order_by invalid value int',
            'order_by invalid value bool',
        ],
    )
    async def test_providers_list_throws(self, providers, parameter, value):
        mock_params = {parameter: value}
        with pytest.raises(InvalidParameterError):
            await providers.list(**mock_params)
