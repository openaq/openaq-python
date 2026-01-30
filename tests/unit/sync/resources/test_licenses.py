from unittest.mock import Mock

import pytest

from openaq._sync.models.licenses import Licenses
from openaq.shared.exceptions import (
    IdentifierOutOfBoundsError,
    InvalidParameterError,
)
from openaq.shared.responses import LicensesResponse


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
                "id": 41,
                "name": "CC BY 4.0",
                "commercialUseAllowed": True,
                "attributionRequired": True,
                "shareAlikeRequired": False,
                "modificationAllowed": True,
                "redistributionAllowed": True,
                "sourceUrl": "https://creativecommons.org/licenses/by/4.0/",
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
                "id": 38,
                "name": "CC0 1.0",
                "commercialUseAllowed": True,
                "attributionRequired": False,
                "shareAlikeRequired": False,
                "modificationAllowed": True,
                "redistributionAllowed": True,
                "sourceUrl": "https://creativecommons.org/publicdomain/zero/1.0/deed.ca",
            },
            {
                "id": 41,
                "name": "CC BY 4.0",
                "commercialUseAllowed": True,
                "attributionRequired": True,
                "shareAlikeRequired": False,
                "modificationAllowed": True,
                "redistributionAllowed": True,
                "sourceUrl": "https://creativecommons.org/licenses/by/4.0/",
            },
        ],
    }
    response.headers = {}

    return response


@pytest.fixture
def licenses(mock_client):
    return Licenses(mock_client)


class TestLicenses:
    def test_get_calls_client_correctly(
        self, licenses, mock_client, mock_single_response
    ):
        mock_client._get.return_value = mock_single_response
        result = licenses.get(41)
        mock_client._get.assert_called_once_with("/licenses/41")
        assert isinstance(result, LicensesResponse)
        assert len(result.results) == 1

    def test_list_with_defaults(self, licenses, mock_client, mock_list_response):
        mock_client._get.return_value = mock_list_response
        result = licenses.list()
        params = mock_client._get.call_args[1]["params"]
        assert mock_client._get.call_args[0][0] == "/licenses"
        assert params["page"] == 1
        assert params["limit"] == 1000
        assert isinstance(result, LicensesResponse)
        assert len(result.results) == 2

    def test_list_with_pagination(self, licenses, mock_client, mock_list_response):
        mock_client._get.return_value = mock_list_response
        licenses.list(page=3, limit=50)
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
        self, licenses, mock_client, mock_list_response, sort_order, expected
    ):
        mock_client._get.return_value = mock_list_response
        licenses.list(order_by="id", sort_order=sort_order)
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
    def test_get_throws(self, licenses, value):
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
    def test_list_throws(self, licenses, parameter, value):
        mock_params = {parameter: value}
        with pytest.raises(InvalidParameterError):
            licenses.list(**mock_params)
