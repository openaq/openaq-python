from openaq.shared.exceptions import IdentifierOutOfBoundsError, InvalidParameterError
from openaq._async.models.manufacturers import Manufacturers
from openaq.shared.responses import InstrumentsResponse, ManufacturersResponse

import pytest
from unittest.mock import AsyncMock, Mock


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
                "id": 5020,
                "name": "MetOne",
                "instruments": [
                    {"id": 13, "name": "AIO 2"},
                    {"id": 14, "name": "BAM 1020"},
                    {"id": 18, "name": "BAM 1022"},
                ],
            },
        ],
    }
    response.headers = {}

    return response


@pytest.fixture
def mock_instruments_response():
    response = Mock()
    response.json.return_value = {
        "meta": {
            "name": "openaq-api",
            "website": "/",
            "page": 1,
            "limit": 100,
            "found": 3,
        },
        "results": [
            {
                "id": 13,
                "name": "AIO 2",
                "isMonitor": True,
                "manufacturer": {"id": 5020, "name": "MetOne"},
            },
            {
                "id": 14,
                "name": "BAM 1020",
                "isMonitor": True,
                "manufacturer": {"id": 5020, "name": "MetOne"},
            },
            {
                "id": 18,
                "name": "BAM 1022",
                "isMonitor": True,
                "manufacturer": {"id": 5020, "name": "MetOne"},
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
                "name": "OpenAQ admin",
                "instruments": [{"id": 1, "name": "N/A"}],
            },
            {
                "id": 5020,
                "name": "MetOne",
                "instruments": [
                    {"id": 13, "name": "AIO 2"},
                    {"id": 14, "name": "BAM 1020"},
                    {"id": 18, "name": "BAM 1022"},
                ],
            },
        ],
    }
    response.headers = {}

    return response


@pytest.fixture
def manufacturers(mock_client):
    return Manufacturers(mock_client)


@pytest.mark.asyncio
class TestManufacturers:
    async def test_get_calls_client_correctly(
        self, manufacturers, mock_client, mock_single_response
    ):
        mock_client._get.return_value = mock_single_response
        result = await manufacturers.get(5020)
        mock_client._get.assert_called_once_with("/manufacturers/5020")
        assert isinstance(result, ManufacturersResponse)
        assert len(result.results) == 1

    async def test_instruments_calls_client_correctly(
        self, manufacturers, mock_client, mock_instruments_response
    ):
        mock_client._get.return_value = mock_instruments_response
        result = await manufacturers.instruments(5020)
        mock_client._get.assert_called_once_with("/manufacturers/5020/instruments")
        assert isinstance(result, InstrumentsResponse)
        assert len(result.results) == 3

    async def test_list_with_defaults(
        self, manufacturers, mock_client, mock_list_response
    ):
        mock_client._get.return_value = mock_list_response
        result = await manufacturers.list()
        params = mock_client._get.call_args[1]["params"]
        assert mock_client._get.call_args[0][0] == "/manufacturers"
        assert params["page"] == 1
        assert params["limit"] == 1000
        assert isinstance(result, ManufacturersResponse)
        assert len(result.results) == 2

    async def test_list_with_pagination(
        self, manufacturers, mock_client, mock_list_response
    ):
        mock_client._get.return_value = mock_list_response
        await manufacturers.list(page=3, limit=50)
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
        self, manufacturers, mock_client, mock_list_response, sort_order, expected
    ):
        mock_client._get.return_value = mock_list_response
        await manufacturers.list(order_by="id", sort_order=sort_order)
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
    async def test_get_throws(self, manufacturers, value):
        with pytest.raises(IdentifierOutOfBoundsError):
            await manufacturers.get(value)

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
    async def test_instruments_throws(self, manufacturers, value):
        with pytest.raises(IdentifierOutOfBoundsError):
            await manufacturers.instruments(value)

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
            ('order_by', False),
        ],
        ids=[
            'page value invalid type',
            'limit value invalid type',
            'limit value out of range',
            'sort_order invalid value, unsupported string',
            'sort_order invalid value int',
            'sort_order invalid value bool',
            'order_by invalid value int',
            'order_by invalid value bool',
        ],
    )
    async def test_list_throws(self, manufacturers, parameter, value):
        mock_params = {parameter: value}
        with pytest.raises(InvalidParameterError):
            await manufacturers.list(**mock_params)
