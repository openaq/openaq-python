from unittest.mock import AsyncMock, Mock

import pytest

from openaq._async.models.countries import Countries
from openaq.shared.exceptions import (
    IdentifierOutOfBoundsError,
    InvalidParameterError,
)
from openaq.shared.responses import CountriesResponse


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
            "limit": 1000,
            "found": 142,
        },
        "results": [
            {
                "id": 1,
                "code": "ID",
                "name": "Indonesia",
                "datetimeFirst": "2016-01-30T01:00:00Z",
                "datetimeLast": "2025-11-26T02:00:00Z",
                "parameters": [
                    {"id": 1, "name": "pm10", "units": "µg/m³", "displayName": None},
                    {"id": 2, "name": "pm25", "units": "µg/m³", "displayName": None},
                ],
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
            "found": 142,
        },
        "results": [
            {
                "id": 1,
                "code": "ID",
                "name": "Indonesia",
                "datetimeFirst": "2016-01-30T01:00:00Z",
                "datetimeLast": "2025-11-26T02:00:00Z",
                "parameters": [
                    {"id": 1, "name": "pm10", "units": "µg/m³", "displayName": None},
                    {"id": 2, "name": "pm25", "units": "µg/m³", "displayName": None},
                ],
            },
            {
                "id": 2,
                "code": "MY",
                "name": "Malaysia",
                "datetimeFirst": "2022-11-03T21:00:00Z",
                "datetimeLast": "2025-11-26T02:00:00Z",
                "parameters": [
                    {"id": 1, "name": "pm10", "units": "µg/m³", "displayName": None},
                    {"id": 2, "name": "pm25", "units": "µg/m³", "displayName": None},
                ],
            },
            {
                "id": 3,
                "code": "CL",
                "name": "Chile",
                "datetimeFirst": "2016-01-30T01:00:00Z",
                "datetimeLast": "2025-11-26T02:00:00Z",
                "parameters": [
                    {"id": 1, "name": "pm10", "units": "µg/m³", "displayName": None},
                    {"id": 2, "name": "pm25", "units": "µg/m³", "displayName": None},
                ],
            },
        ],
    }
    response.headers = {}

    return response


@pytest.fixture
def countries(mock_client):
    return Countries(mock_client)


@pytest.mark.asyncio
class TestCountries:
    async def test_get_calls_client_correctly(
        self, countries, mock_client, mock_single_response
    ):
        mock_client._get.return_value = mock_single_response
        result = await countries.get(1)
        mock_client._get.assert_called_once_with("/countries/1")
        assert isinstance(result, CountriesResponse)
        assert len(result.results) == 1

    async def test_list_with_defaults(self, countries, mock_client, mock_list_response):
        mock_client._get.return_value = mock_list_response
        result = await countries.list()
        params = mock_client._get.call_args[1]["params"]
        assert mock_client._get.call_args[0][0] == "/countries"
        assert params["page"] == 1
        assert params["limit"] == 1000
        assert isinstance(result, CountriesResponse)
        assert len(result.results) == 3

    async def test_list_with_pagination(
        self, countries, mock_client, mock_list_response
    ):
        mock_client._get.return_value = mock_list_response
        await countries.list(page=3, limit=50)
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
        self, countries, mock_client, mock_list_response, sort_order, expected
    ):
        mock_client._get.return_value = mock_list_response
        await countries.list(order_by="id", sort_order=sort_order)
        params = mock_client._get.call_args[1]["params"]
        assert params["order_by"] == "id"
        assert params["sort_order"] == expected

    @pytest.mark.parametrize(
        "parameters_id,providers_id",
        [
            (1, 5),
            ([1, 2, 3], [4, 5, 6]),
        ],
    )
    async def test_list_with_filters(
        self,
        countries,
        mock_client,
        mock_list_response,
        parameters_id,
        providers_id,
    ):
        mock_client._get.return_value = mock_list_response
        await countries.list(parameters_id=parameters_id, providers_id=providers_id)
        params = mock_client._get.call_args[1]["params"]
        assert "parameters_id" in params
        assert "providers_id" in params

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
    async def test_countries_get_throws(self, countries, value):
        with pytest.raises(IdentifierOutOfBoundsError):
            await countries.get(value)

    @pytest.mark.parametrize(
        "parameter,value",
        [
            ('page', '1'),
            ('limit', '1000'),
            ('limit', 9999),
            ('parameters_id', 2**31),
            ('parameters_id', '999'),
            ('parameters_id', [1, 2, 3, '4']),
            ('parameters_id', [1, 2, 3, 2**31]),
            ('parameters_id', True),
            ('providers_id', 2**31),
            ('providers_id', '999'),
            ('providers_id', [1, 2, 3, '4']),
            ('providers_id', [1, 2, 3, 2**31]),
            ('providers_id', True),
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
            'order_by invalid value bool',
        ],
    )
    async def test_countries_list_throws(self, countries, parameter, value):
        mock_params = {parameter: value}
        with pytest.raises(InvalidParameterError):
            await countries.list(**mock_params)
