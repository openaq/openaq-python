from __future__ import annotations

import datetime
from typing import Union

from openaq.shared.exceptions import NotFoundError
from openaq.shared.models import build_query_params
from openaq.shared.responses import MeasurementsResponse
from openaq.shared.types import Rollup, Data

from .base import SyncResourceBase


class Measurements(SyncResourceBase):
    """This provides methods to retrieve and list the air quality measurements from the OpenAQ API."""

    def list(
        self,
        sensors_id: int,
        date_from: Union[datetime.datetime, str, None] = "2016-10-10",
        date_to: Union[datetime.datetime, str, None] = None,
        data: Union[Data, None] = None,
        rollup: Union[Rollup, None] = None,
        page: int = 1,
        limit: int = 1000,
    ) -> MeasurementsResponse:
        """List air quality measurements based on provided filters.

        Provides the ability to filter the measurements resource by sensor, date range,
        pagination settings.

        * `sensors_id` - Filters measurements to a specific sensors ID (required)
        * `date_from` - Declare a start time for data retrieval
        * `date_to` - Declare an end time or data retrieval
        * `page` - Specifies the page number of results to retrieve
        * `limit` - Sets the number of results generated per page

        Args:
            sensors_id: The ID of the sensor for which measurements should be retrieved.
            date_from: Starting date for the measurement retrieval. Can be a datetime object or ISO-8601 formatted date or datetime string.
            date_to: Ending date for the measurement retrieval. Can be a datetime object or ISO-8601 formatted date or datetime string.
            page: The page number to fetch. Page count is determined by total measurements found divided by the limit.
            limit: The number of results returned per page.

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
            date_from=date_from,
            date_to=date_to,
        )
        base_path = f'/sensors/{sensors_id}'
        if data == 'measurements' or data == None:
            path = base_path + '/measurements'
        if data == 'hours':
            path = base_path + '/hours'
        if data == 'days':
            path = base_path + '/days'
        if data == 'years':
            path = base_path + '/years'
        if rollup:
            path += f'/{rollup}'
        if data == 'hours' and rollup == 'hourly':
            raise NotFoundError()
        if data == 'days' and rollup == 'daily':
            raise NotFoundError()
        if data == 'years' and rollup == 'yearly':
            raise NotFoundError()

        measurements_response = self._client._get(path, params=params)

        return MeasurementsResponse.read_response(measurements_response)
