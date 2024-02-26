from __future__ import annotations

from openaq.shared.responses import SensorsResponse

from .base import AsyncResourceBase


class Sensors(AsyncResourceBase):
    """This provides methods to retrieve sensor data from the OpenAQ API."""

    async def get(self, sensors_id: int) -> SensorsResponse:
        """Retrieve a specific sensor by its ID.

        Args:
            sensors_id: The ID of the sensor to retrieve.

        Returns:
            SensorsResponse: An instance representing the retrieved sensor.
        """
        sensor = await self._client._get(f"/sensors/{sensors_id}")
        return SensorsResponse.load(sensor.json())

    async def list(self, locations_id: int) -> SensorsResponse:
        """Retrieve sensors for a specific location by its ID.

        Args:
            locations_id: The ID of the location to retrieve sensors for.

        Returns:
            SensorsResponse: An instance representing the sensors associated with the location.
        """
        sensors = await self._client._get(f"/locations/{locations_id}/sensors")
        return SensorsResponse.load(sensors.json())
