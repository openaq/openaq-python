from __future__ import annotations

import datetime
from typing import List, Union

from openaq.shared.models import build_query_params
from openaq.shared.responses import MeasurementsResponse

from .base import SyncResourceBase


class Measurements(SyncResourceBase):
    """This provides methods to retrieve and list the air quality measurements from the OpenAQ API."""

    def list(
        self,
        locations_id: int,
        date_from: Union[datetime.datetime, str, None] = "2016-10-10",
        date_to: Union[datetime.datetime, str, None] = None,
        page: int = 1,
        limit: int = 1000,
        parameters_id: Union[int, List[int], None] = None,
    ) -> MeasurementsResponse:
        """List air quality measurements based on provided filters.

        Provides the ability to filter the measurements resource by location, date range,
        pagination settings, and specific parameters.

        * `locations_id` - Filters measurements to a specific locations ID (required)
        * `date_from` - Declare a start time for data retrieval
        * `date_to` - Declare an end time or data retrieval
        * `page` - Specifies the page number of results to retrieve
        * `limit` - Sets the number of results generated per page
        * `parameters_id` - Filters results by selected parameters ID(s)

        Args:
            locations_id: The ID of the location for which measurements should be retrieved.
            date_from: Starting date for the measurement retrieval. Can be a datetime object or ISO-8601 formatted date or datetime string.
            date_to: Ending date for the measurement retrieval. Can be a datetime object or ISO-8601 formatted date or datetime string.
            page: The page number to fetch. Page count is determined by total measurements found divided by the limit.
            limit: The number of results returned per page.
            parameters_id: Single parameters ID or an array of IDs.

        Returns:
            MeasurementsResponse: An instance representing the list of retrieved air quality measurements.

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
        params = build_query_params(
            page=page,
            limit=limit,
            locations_id=locations_id,
            date_from=date_from,
            date_to=date_to,
            parameters_id=parameters_id,
        )

        measurements = self._client._get(
            f"/locations/{locations_id}/measurements", params=params
        )
        return MeasurementsResponse.load(measurements.json())
