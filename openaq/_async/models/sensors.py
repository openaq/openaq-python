from openaq.shared.responses import SensorsResponse

from .base import AsyncResourceBase


class Sensors(AsyncResourceBase):
    """This provides methods to retrieve sensor data from the OpenAQ API."""

    async def get(self, sensors_id: int) -> SensorsResponse:
        """Retrieve specific sensor data by its sensors ID.

        Args:
            sensors_id: The sensors ID of the sensor to retrieve.

        Returns:
            SensorsResponse: An instance representing the retrieved sensor.

        Raises:
            AuthError: Authentication error, improperly supplied credentials.
            BadRequestError: Raised for HTTP 400 error, indicating a client request error.
            NotAuthorizedError: Raised for HTTP 401 error, indicating the client is not authorized.
            ForbiddenError: Raised for HTTP 403 error, indicating the request is forbidden.
            NotFoundError: Raised for HTTP 404 error, indicating a resource is not found.
            ValidationError: Raised for HTTP 422 error, indicating invalid request parameters.
            RateLimitError: Raised when managed client exceeds rate limit.
            HTTPRateLimitError: Raised for HTTP 429 error, indicating rate limit exceeded.
            ServerError: Raised for HTTP 500 error, indicating an internal server error or unexpected server-side issue.
            BadGatewayError: Raised for HTTP 502, indicating that the gateway or proxy received an invalid response from the upstream server.
            ServiceUnavailableError: Raised for HTTP 503, indicating that the server is not ready to handle the request.
            GatewayTimeoutError: Raised for HTTP 504 error, indicating a gateway timeout.
        """
        sensor_response = await self._client._get(f"/sensors/{sensors_id}")
        return SensorsResponse.read_response(sensor_response)
