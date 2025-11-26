from openaq.shared.exceptions import IdentifierOutOfBoundsError, InvalidParameterError
from openaq._async.models.sensors import Sensors
from openaq.shared.responses import SensorsResponse

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
                    "utc": "2025-11-26T15:00:00Z",
                    "local": "2025-11-26T08:00:00-07:00",
                },
                "coverage": {
                    "expectedCount": 1,
                    "expectedInterval": "01:00:00",
                    "observedCount": 66561,
                    "observedInterval": "66561:00:00",
                    "percentComplete": 6656100,
                    "percentCoverage": 6656100,
                    "datetimeFrom": {
                        "utc": "2016-03-06T20:00:00Z",
                        "local": "2016-03-06T13:00:00-07:00",
                    },
                    "datetimeTo": {
                        "utc": "2025-11-26T15:00:00Z",
                        "local": "2025-11-26T08:00:00-07:00",
                    },
                },
                "latest": {
                    "datetime": {
                        "utc": "2025-11-26T15:00:00Z",
                        "local": "2025-11-26T08:00:00-07:00",
                    },
                    "value": 4.9,
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
def sensors(mock_client):
    return Sensors(mock_client)


@pytest.mark.asyncio
class TestSensors:
    async def test_get_calls_client_correctly(
        self, sensors, mock_client, mock_single_response
    ):
        mock_client._get.return_value = mock_single_response
        result = await sensors.get(3920)
        mock_client._get.assert_called_once_with("/sensors/3920")
        assert isinstance(result, SensorsResponse)
        assert len(result.results) == 1

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
    async def test_get_throws(self, sensors, value):
        with pytest.raises(IdentifierOutOfBoundsError):
            await sensors.get(value)
