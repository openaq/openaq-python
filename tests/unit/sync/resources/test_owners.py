from openaq.shared.exceptions import IdentifierOutOfBoundsError, InvalidParameterError
from openaq._sync.models.owners import Owners
from openaq.shared.responses import OwnersResponse

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
            "found": ">100",
        },
        "results": [{"id": 1, "name": "OpenAQ admin"}],
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
            "found": 3,
        },
        "results": [
            {"id": 1, "name": "OpenAQ admin"},
            {"id": 4, "name": "Unknown Governmental Organization"},
            {"id": 5, "name": "Unknown Research Organization"},
        ],
    }
    response.headers = {}

    return response


@pytest.fixture
def owners(mock_client):
    return Owners(mock_client)


class TestOwners:
    def test_get_calls_client_correctly(
        self, owners, mock_client, mock_single_response
    ):
        mock_client._get.return_value = mock_single_response
        result = owners.get(1)
        mock_client._get.assert_called_once_with("/owners/1")
        assert isinstance(result, OwnersResponse)
        assert len(result.results) == 1

    def test_list_with_defaults(self, owners, mock_client, mock_list_response):
        mock_client._get.return_value = mock_list_response
        result = owners.list()
        params = mock_client._get.call_args[1]["params"]
        assert mock_client._get.call_args[0][0] == "/owners"
        assert params["page"] == 1
        assert params["limit"] == 1000
        assert isinstance(result, OwnersResponse)
        assert len(result.results) == 3

    def test_list_with_pagination(self, owners, mock_client, mock_list_response):
        mock_client._get.return_value = mock_list_response
        owners.list(page=3, limit=50)
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
        self, owners, mock_client, mock_list_response, sort_order, expected
    ):
        mock_client._get.return_value = mock_list_response
        owners.list(order_by="id", sort_order=sort_order)
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
    def test_owners_get_throws(self, owners, value):
        with pytest.raises(IdentifierOutOfBoundsError):
            owners.get(value)

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
    def test_owners_list_throws(self, owners, parameter, value):
        mock_params = {parameter: value}
        with pytest.raises(InvalidParameterError):
            owners.list(**mock_params)
