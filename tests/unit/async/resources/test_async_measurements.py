import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from openaq._async.models.measurements import Measurements
from openaq.shared.exceptions import (
    IdentifierOutOfBoundsError,
    InvalidParameterError,
)
from openaq.shared.responses import MeasurementsResponse


@pytest.fixture
def mock_client():
    return AsyncMock()


@pytest.fixture
def mock_measurements_response():
    response = Mock()
    response.json.return_value = {
        "meta": {
            "name": "openaq-api",
            "website": "/",
            "page": 1,
            "limit": 100,
            "found": ">100",
        },
        "results": [
            {
                "value": -0.1,
                "flagInfo": {"hasFlags": False},
                "parameter": {
                    "id": 2,
                    "name": "pm25",
                    "units": "µg/m³",
                    "displayName": None,
                },
                "period": {
                    "label": "raw",
                    "interval": "01:00:00",
                    "datetimeFrom": {
                        "utc": "2016-03-06T19:00:00Z",
                        "local": "2016-03-06T12:00:00-07:00",
                    },
                    "datetimeTo": {
                        "utc": "2016-03-06T20:00:00Z",
                        "local": "2016-03-06T13:00:00-07:00",
                    },
                },
                "coordinates": None,
                "summary": None,
                "coverage": {
                    "expectedCount": 1,
                    "expectedInterval": "01:00:00",
                    "observedCount": 1,
                    "observedInterval": "01:00:00",
                    "percentComplete": 100,
                    "percentCoverage": 100,
                    "datetimeFrom": {
                        "utc": "2016-03-06T19:00:00Z",
                        "local": "2016-03-06T12:00:00-07:00",
                    },
                    "datetimeTo": {
                        "utc": "2016-03-06T20:00:00Z",
                        "local": "2016-03-06T13:00:00-07:00",
                    },
                },
            },
            {
                "value": 1.1,
                "flagInfo": {"hasFlags": False},
                "parameter": {
                    "id": 2,
                    "name": "pm25",
                    "units": "µg/m³",
                    "displayName": None,
                },
                "period": {
                    "label": "raw",
                    "interval": "01:00:00",
                    "datetimeFrom": {
                        "utc": "2016-03-06T20:00:00Z",
                        "local": "2016-03-06T13:00:00-07:00",
                    },
                    "datetimeTo": {
                        "utc": "2016-03-06T21:00:00Z",
                        "local": "2016-03-06T14:00:00-07:00",
                    },
                },
                "coordinates": None,
                "summary": None,
                "coverage": {
                    "expectedCount": 1,
                    "expectedInterval": "01:00:00",
                    "observedCount": 1,
                    "observedInterval": "01:00:00",
                    "percentComplete": 100,
                    "percentCoverage": 100,
                    "datetimeFrom": {
                        "utc": "2016-03-06T20:00:00Z",
                        "local": "2016-03-06T13:00:00-07:00",
                    },
                    "datetimeTo": {
                        "utc": "2016-03-06T21:00:00Z",
                        "local": "2016-03-06T14:00:00-07:00",
                    },
                },
            },
        ],
    }
    response.headers = {}
    return response


@pytest.fixture
def measurements(mock_client):
    return Measurements(mock_client)


@pytest.mark.asyncio
class TestMeasurements:
    async def test_list_with_defaults(
        self, measurements, mock_client, mock_measurements_response
    ):
        mock_client._get.return_value = mock_measurements_response
        result = await measurements.list(sensors_id=123, data='measurements')

        params = mock_client._get.call_args[1]["params"]
        path = mock_client._get.call_args[0][0]

        assert path == "/sensors/123/measurements"
        assert params["page"] == 1
        assert params["limit"] == 1000
        assert "datetime_from" not in params
        assert "datetime_to" not in params
        assert "date_from" not in params
        assert "date_to" not in params
        assert isinstance(result, MeasurementsResponse)
        assert len(result.results) == 2

    async def test_list_with_pagination(
        self, measurements, mock_client, mock_measurements_response
    ):
        mock_client._get.return_value = mock_measurements_response
        await measurements.list(sensors_id=123, data='measurements', page=3, limit=50)

        params = mock_client._get.call_args[1]["params"]
        assert params["page"] == 3
        assert params["limit"] == 50

    async def test_list_with_datetime_from_as_string(
        self, measurements, mock_client, mock_measurements_response
    ):
        mock_client._get.return_value = mock_measurements_response
        await measurements.list(
            sensors_id=123, data='measurements', datetime_from="2024-01-01"
        )

        params = mock_client._get.call_args[1]["params"]
        assert params["datetime_from"] == "2024-01-01T00:00:00"

    async def test_list_with_datetime_from_as_datetime(
        self, measurements, mock_client, mock_measurements_response
    ):
        mock_client._get.return_value = mock_measurements_response
        dt = datetime.datetime(2024, 1, 1, 12, 30, 0)
        await measurements.list(sensors_id=123, data='measurements', datetime_from=dt)

        params = mock_client._get.call_args[1]["params"]
        assert "2024-01-01" in params["datetime_from"]

    async def test_list_with_datetime_to_as_string(
        self, measurements, mock_client, mock_measurements_response
    ):
        mock_client._get.return_value = mock_measurements_response
        await measurements.list(
            sensors_id=123,
            data='measurements',
            datetime_from="2024-01-01",
            datetime_to="2024-01-31",
        )

        params = mock_client._get.call_args[1]["params"]
        assert params["datetime_from"] == "2024-01-01T00:00:00"
        assert params["datetime_to"] == "2024-01-31T00:00:00"

    async def test_list_with_datetime_to_as_datetime(
        self, measurements, mock_client, mock_measurements_response
    ):
        mock_client._get.return_value = mock_measurements_response
        dt_from = datetime.datetime(2024, 1, 1)
        dt_to = datetime.datetime(2024, 1, 31)
        await measurements.list(
            sensors_id=123,
            data='measurements',
            datetime_from=dt_from,
            datetime_to=dt_to,
        )

        params = mock_client._get.call_args[1]["params"]
        assert "2024-01-01" in params["datetime_from"]
        assert "2024-01-31" in params["datetime_to"]

    @pytest.mark.parametrize(
        "data, rollup",
        [
            ("measurements", "hourly"),
            ("measurements", "daily"),
            ("hours", "daily"),
            ("hours", "yearly"),
            ("days", "yearly"),
        ],
        ids=[
            "measurements hourly",
            "measurements daily",
            "hours daily",
            "hours yearly",
            "days yearly",
        ],
    )
    async def test_list_with_data_rollup_parameter(
        self, measurements, mock_client, mock_measurements_response, data, rollup
    ):
        mock_client._get.return_value = mock_measurements_response
        await measurements.list(sensors_id=123, data=data, rollup=rollup)

        path = mock_client._get.call_args[0][0]
        assert path == f"/sensors/123/{data}/{rollup}"

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
    async def test_list_invalid_sensors_id(self, measurements, value):
        with pytest.raises(IdentifierOutOfBoundsError):
            await measurements.list(sensors_id=value, data="measurements")

    @pytest.mark.parametrize(
        "parameter,value",
        [
            ('page', '1'),
            ('page', 0),
            ('page', -1),
            ('limit', '1000'),
            ('limit', 0),
            ('limit', 1001),
            ('limit', -1),
        ],
        ids=[
            'page value invalid type',
            'page value zero',
            'page value negative',
            'limit value invalid type',
            'limit value zero',
            'limit value out of range high',
            'limit value negative',
        ],
    )
    async def test_list_invalid_pagination_params(self, measurements, parameter, value):
        mock_params = {'sensors_id': 123, 'data': 'measurements', parameter: value}
        with pytest.raises(InvalidParameterError):
            await measurements.list(**mock_params)

    @pytest.mark.parametrize(
        "data_value",
        ['invalid_data', 123, True, False],
        ids=[
            'data invalid string',
            'data invalid type int',
            'data invalid type bool True',
            'data invalid type bool False',
        ],
    )
    async def test_list_invalid_data_param(self, measurements, data_value):
        with pytest.raises(InvalidParameterError):
            await measurements.list(sensors_id=123, data=data_value)

    @pytest.mark.parametrize(
        "rollup_value",
        ['invalid_rollup', 123, True, False],
        ids=[
            'rollup invalid string',
            'rollup invalid type int',
            'rollup invalid type bool True',
            'rollup invalid type bool False',
        ],
    )
    async def test_list_invalid_rollup_param(self, measurements, rollup_value):
        with pytest.raises(InvalidParameterError):
            await measurements.list(
                sensors_id=123, data='measurements', rollup=rollup_value
            )

    @pytest.mark.parametrize(
        "datetime_from,datetime_to",
        [
            ('invalid-date', None),
            (None, 'invalid-date'),
            ('2024-13-01', None),
            ('2024-01-32', None),
            (123, None),
            (None, 123),
            (True, None),
            (None, False),
        ],
        ids=[
            'datetime_from invalid format',
            'datetime_to invalid format',
            'datetime_from invalid month',
            'datetime_from invalid day',
            'datetime_from invalid type int',
            'datetime_to invalid type int',
            'datetime_from invalid type bool',
            'datetime_to invalid type bool',
        ],
    )
    async def test_list_invalid_datetime_params(
        self, measurements, mock_client, datetime_from, datetime_to
    ):
        with pytest.raises(InvalidParameterError):
            await measurements.list(
                sensors_id=123,
                data='measurements',
                datetime_from=datetime_from,
                datetime_to=datetime_to,
            )
        mock_client._get.assert_not_called()

    async def test_list_date_overload_uses_date_params(
        self, measurements, mock_client, mock_measurements_response
    ):
        mock_client._get.return_value = mock_measurements_response

        await measurements.list(
            sensors_id=123,
            data='days',
            date_from="2026-01-01",
            date_to="2026-02-12",
        )

        params = mock_client._get.call_args[1]["params"]
        assert "date_from" in params
        assert "date_to" in params
        assert "datetime_from" not in params
        assert "datetime_to" not in params

    @pytest.mark.parametrize(
        "data",
        [
            pytest.param("days", id="days-DateData"),
            pytest.param("years", id="years-DateData"),
        ],
    )
    async def test_list_date_overload_accepts_date_params(
        self, measurements, mock_client, mock_measurements_response, data
    ):
        mock_client._get.return_value = mock_measurements_response

        date_from = datetime.date(2026, 1, 1)
        date_to = datetime.date(2024, 2, 12)

        await measurements.list(
            sensors_id=123,
            data=data,
            date_from=date_from,
            date_to=date_to,
        )

        params = mock_client._get.call_args[1]["params"]
        assert "date_from" in params
        assert "date_to" in params
