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
        sensors_id: int,
        date_from: Union[datetime.datetime, str, None] = "2016-10-10",
        date_to: Union[datetime.datetime, str, None] = None,
        page: int = 1,
        limit: int = 1000,
    ) -> MeasurementsResponse:
        """List air quality measurements based on provided filters.

        Provides the ability to filter the measurements resource by location, date range,
        pagination settings, and specific parameters.

        * `sensors_id` - Filters measurements to a specific sensor ID (required)
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
            sensors_id=sensors_id,
            date_from=date_from,
            date_to=date_to,
        )

        measurements = self._client._get(
            f"/sensors/{sensors_id}/measurements", params=params
        )
        return MeasurementsResponse.load(measurements.json())

    def list_by_location(
        self,
        locations_id: int,
        date_from: Union[datetime.datetime, str, None] = "2016-10-10",
        date_to: Union[datetime.datetime, str, None] = None,
        page: int = 1,
        limit: int = 1000,
        parameters_id: Union[int, List[int], None] = None,
    ) -> MeasurementsResponse:
        """List air quality measurements for a specific location.

        Provides the ability to filter the measurements resource by location, date range,
        pagination settings, and specific parameters.

        * `locations_id` - Filters measurements to a specific location ID (required)
        * `date_from` - Declare a start time for data retrieval
        * `date_to` - Declare an end time or data retrieval
        * `page` - Specifies the page number of results to retrieve
        * `limit` - Sets the number of results generated per page
        * `parameters_id` - Single parameters ID or an array of IDs

        Args:
            locations_id: The ID of the location for which measurements should be retrieved.
            date_from: Starting date for the measurement retrieval. Can be a datetime object or ISO-8601 formatted date or datetime string.
            date_to: Ending date for the measurement retrieval. Can be a datetime object or ISO-8601 formatted date or datetime string.
            page: The page number to fetch. Page count is determined by total measurements found divided by the limit.
            limit: The number of results returned per page.
            parameters_id: Single parameters ID or a list of IDs to filter the measurements.

        Returns:
            MeasurementsResponse: An instance representing the list of retrieved air quality measurements for the specified location.

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
        location = self._client._get(f"/locations/{locations_id}")
        location_data = location.json()
        location_obj = location_data["results"][0]
        sensor_ids = [sensor["id"] for sensor in location_obj["sensors"]]

        if parameters_id:
            if isinstance(parameters_id, int):
                parameters_id = [parameters_id]
            sensor_ids = [
                sensor_id
                for sensor_id in sensor_ids
                if any(
                    sensor["parameter"]["id"] in parameters_id
                    for sensor in location_obj["sensors"]
                    if sensor["id"] == sensor_id
                )
            ]

        measurements = []
        for sensor_id in sensor_ids:
            params = build_query_params(
                page=page,
                limit=limit,
                date_from=date_from,
                date_to=date_to,
                parameters_id=parameters_id,
            )
            sensor_measurements = self._client._get(
                f"/sensors/{sensor_id}/measurements", params=params
            )
            measurements.extend(sensor_measurements.json()["results"])

        response_data = {
            "meta": {
                "name": "openaq-api",
                "license": "CC BY 4.0",
                "website": "https://u50g7n0cbj.execute-api.us-east-1.amazonaws.com/",
                "page": 1,
                "limit": len(measurements),
                "found": len(measurements),
            },
            "results": measurements,
        }
        return MeasurementsResponse.load(response_data)
