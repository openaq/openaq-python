from openaq.shared.exceptions import IdentifierOutOfBoundsError, InvalidParameterError
from openaq._sync.models.instruments import Instruments
from openaq.shared.responses import InstrumentsResponse

import pytest
from unittest.mock import Mock


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
            "found": 24,
        },
        "results": [
            {
                "id": 12,
                "name": "MA350",
                "isMonitor": True,
                "manufacturer": {"id": 5021, "name": "AethLabs"},
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
            "found": 24,
        },
        "results": [
            {
                "id": 12,
                "name": "MA350",
                "isMonitor": True,
                "manufacturer": {"id": 5021, "name": "AethLabs"},
            },
            {
                "id": 13,
                "name": "AIO 2",
                "isMonitor": True,
                "manufacturer": {"id": 5020, "name": "MetOne"},
            },
        ],
    }
    response.headers = {}

    return response


@pytest.fixture
def instruments(mock_client):
    return Instruments(mock_client)


class TestInstruments:
    def test_get_calls_client_correctly(
        self, instruments, mock_client, mock_single_response
    ):
        mock_client._get.return_value = mock_single_response
        result = instruments.get(12)
        mock_client._get.assert_called_once_with("/instruments/12")
        assert isinstance(result, InstrumentsResponse)
        assert len(result.results) == 1

    def test_list_with_defaults(self, instruments, mock_client, mock_list_response):
        mock_client._get.return_value = mock_list_response
        result = instruments.list()
        params = mock_client._get.call_args[1]["params"]
        assert mock_client._get.call_args[0][0] == "/instruments"
        assert params["page"] == 1
        assert params["limit"] == 1000
        assert isinstance(result, InstrumentsResponse)
        assert len(result.results) == 2

    def test_list_with_pagination(self, instruments, mock_client, mock_list_response):
        mock_client._get.return_value = mock_list_response
        instruments.list(page=3, limit=50)
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
        self, instruments, mock_client, mock_list_response, sort_order, expected
    ):
        mock_client._get.return_value = mock_list_response
        instruments.list(order_by="id", sort_order=sort_order)
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
    def test_instruments_get_throws(self, instruments, value):
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
    def test_instruments_list_throws(self, instruments, parameter, value):
        mock_params = {parameter: value}
        with pytest.raises(InvalidParameterError):
            instruments.list(**mock_params)
