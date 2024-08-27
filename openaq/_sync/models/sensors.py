from openaq.shared.responses import SensorsResponse

from .base import SyncResourceBase


class Sensors(SyncResourceBase):
    """This provides methods to retrieve sensor data from the OpenAQ API."""

    def get(self, sensors_id: int) -> SensorsResponse:
        """Retrieve specific sensor data by its sensors ID.

        Args:
            sensors_id: The sensors ID of the sensor to retrieve.

        Returns:
            SensorsResponse: An instance representing the retrieved sensor.

        Raises:
            BadRequestError: Raised for HTTP 400 error, indicating a client request error.
            NotAuthorized: Raised for HTTP 401 error, indicating the client is not authorized.
            Forbidden: Raised for HTTP 403 error, indicating the request is forbidden.
            NotFoundError: Raised for HTTP 404 error, indicating a resource is not found.
            ValidationError: Raised for HTTP 422 error, indicating invalid request parameters.
            RateLimit: Raised for HTTP 429 error, indicating rate limit exceeded.
            ServerError: Raised for HTTP 500 error, indicating an internal server error or unexpected server-side issue.
            GatewayTimeoutError: Raised for HTTP 504 error, indicating a gateway timeout.
        """
        sensor_response = self._client._get(f"/sensors/{sensors_id}")
        return SensorsResponse.read_response(sensor_response)
