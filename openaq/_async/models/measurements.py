from __future__ import annotations

import datetime

from openaq.shared.models import build_measurements_path, build_query_params
from openaq.shared.responses import MeasurementsResponse
from openaq.shared.types import Data, Rollup

from .base import AsyncResourceBase


class Measurements(AsyncResourceBase):
    """This provides methods to retrieve and list the air quality measurements from the OpenAQ API."""

    async def list(
        self,
        sensors_id: int,
        data: Data | None = None,
        rollup: Rollup | None = None,
        date_from: datetime.datetime | str | None = "2016-10-10",
        date_to: datetime.datetime | str | None = None,
        page: int = 1,
        limit: int = 1000,
    ) -> MeasurementsResponse:
        """List air quality measurements based on provided filters.

        Provides the ability to filter the measurements resource by location, date range,
        pagination settings, and specific parameters.

        * `sensors_id` - Filters measurements to a specific sensors ID (required)
        * `data` - the base measurement unit to query. options are 'measurements', 'hours', 'days', 'years'
        * `rollup` - the period by which to rollup the base measurement data. Options are 'hourly', 'daily', 'yearly'
        * `date_from` - Declare a start time for data retrieval
        * `date_to` - Declare an end time or data retrieval
        * `page` - Specifies the page number of results to retrieve
        * `limit` - Sets the number of results generated per page

        Args:
            sensors_id: The ID of the sensor for which measurements should be retrieved.
            data: The base measurement unit to query
            rollup: The period by which to rollup the base measurement data.
            date_from: Starting date for the measurement retrieval. Can be a datetime object or ISO-8601 formatted date or datetime string.
            date_to: Ending date for the measurement retrieval. Can be a datetime object or ISO-8601 formatted date or datetime string.
            page: The page number to fetch. Page count is determined by total measurements found divided by the limit.
            limit: The number of results returned per page.

        Returns:
            MeasurementsResponse: An instance representing the list of retrieved air quality measurements.

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
        params = build_query_params(
            page=page, limit=limit, date_from=date_from, date_to=date_to
        )
        path = build_measurements_path(sensors_id, data, rollup)

        measurements = await self._client._get(path, params=params)
        return MeasurementsResponse.read_response(measurements)
