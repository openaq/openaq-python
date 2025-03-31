from __future__ import annotations

from typing import Tuple

from openaq.shared.models import build_query_params
from openaq.shared.responses import (
    LatestResponse,
    LocationsResponse,
    SensorsResponse,
)

from .base import AsyncResourceBase


class Locations(AsyncResourceBase):
    """This provides methods to retrieve air monitor locations resource from the OpenAQ API."""

    async def get(self, locations_id: int) -> LocationsResponse:
        """Retrieve a specific location by its locations ID.

        Args:
            locations_id: The locations ID of the location to retrieve.

        Returns:
            LocationsResponse: An instance representing the retrieved location.

        Raises:
            BadRequestError: Raised for HTTP 400 error, indicating a client request error.
            NotAuthorizedError: Raised for HTTP 401 error, indicating the client is not authorized.
            ForbiddenError: Raised for HTTP 403 error, indicating the request is forbidden.
            NotFoundError: Raised for HTTP 404 error, indicating a resource is not found.
            ValidationError: Raised for HTTP 422 error, indicating invalid request parameters.
            RateLimitError: Raised for HTTP 429 error, indicating rate limit exceeded.
            ServerError: Raised for HTTP 500 error, indicating an internal server error or unexpected server-side issue.
            GatewayTimeoutError: Raised for HTTP 504 error, indicating a gateway timeout.
        """
        location = await self._client._get(f"/locations/{locations_id}")
        return LocationsResponse.read_response(location)

    async def latest(self, locations_id: int) -> LatestResponse:
        """Retrieve latest measurements from a location.

        Args:
            locations_id: The locations ID of the location to retrieve.

        Returns:
            LatestResponse: An instance representing the retrieved latest results.

        Raises:
            BadRequestError: Raised for HTTP 400 error, indicating a client request error.
            NotAuthorizedError: Raised for HTTP 401 error, indicating the client is not authorized.
            ForbiddenError: Raised for HTTP 403 error, indicating the request is forbidden.
            NotFoundError: Raised for HTTP 404 error, indicating a resource is not found.
            ValidationError: Raised for HTTP 422 error, indicating invalid request parameters.
            RateLimitError: Raised for HTTP 429 error, indicating rate limit exceeded.
            ServerError: Raised for HTTP 500 error, indicating an internal server error or unexpected server-side issue.
            GatewayTimeoutError: Raised for HTTP 504 error, indicating a gateway timeout.
        """
        latest = await self._client._get(f"/locations/{locations_id}/latest")
        return LatestResponse.read_response(latest)

    async def list(
        self,
        page: int = 1,
        limit: int = 100,
        radius: int | None = None,
        coordinates: Tuple[float, float] | None = None,
        bbox: Tuple[float, float, float, float] | None = None,
        providers_id: int | list[int] | None = None,
        countries_id: int | list[int] | None = None,
        parameters_id: int | list[int] | None = None,
        licenses_id: int | list[int] | None = None,
        iso: str | None = None,
        monitor: bool | None = None,
        mobile: bool | None = None,
        order_by: str | None = None,
        sort_order: str | None = None,
    ) -> LocationsResponse:
        """List locations based on provided filters.

        Provides the ability to filter the locations resource by the given arguments.

        * `page` - Specifies the page number of results to retrieve
        * `limit` - Sets the number of results generated per page
        * `radius` - Specifies the distance around a central point, filtering locations within a circular area. Must be used with `coordinates`, cannot be used in combination with `bbox`
        * `coordinates` - Filters locations by coordinates. Must be used with `radius`, cannot be used in combination with `bbox`
        * `bbox` - Filters locations using a bounding box. Cannot be used with `coordinates` or `radius`
        * `providers_id` - Filters results by selected providers ID(s)
        * `countries_id` - Filters results by selected countries ID(s)
        * `parameters_id` - Filters results by selected parameters ID(s)
        * `licenses_id` - Filters results by selected licenses ID(s)
        * `iso` - Filters results by selected country code
        * `monitor` - Filters results by reference grade monitors (`true`), air sensors (`false`), or both if not used
        * `mobile` - Filters results for mobile sensors (`true`), non-mobile sensors (`false`), or both if not used
        * `order_by` - Determines the fields by which results are sorted; available values are `id`
        * `sort_order` - Works in tandem with `order_by` to specify the direction: either `asc` (ascending) or `desc` (descending)

        Args:
            page: The page number. Page count is locations found / limit.
            limit: The number of results returned per page.
            radius: A distance value in meters to search around the given coordinates value.
            coordinates: WGS 84 coordinate pair in form latitude, longitude (y,x).
            bbox: Geospatial bounding box of min X, min Y, max X, max Y in WGS 84 coordinates. Limited to four decimals precision.
            providers_id: Single providers ID or an array of IDs.
            countries_id: Single countries ID or an array of IDs.
            parameters_id: Single parameters ID or an array of IDs.
            licenses_id: Single licenses ID or an array of IDs.
            iso: 2 letter ISO 3166-alpha-2 country code.
            monitor: Boolean for reference grade monitors (true) or air sensors (false)
            mobile: Boolean mobile locations (true) or not mobile locations (false).
            order_by: Order by operators for results.
            sort_order: Sort order (asc/desc).

        Returns:
            LocationsResponse: An instance representing the list of retrieved locations.

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
            page=page,
            limit=limit,
            radius=radius,
            coordinates=coordinates,
            bbox=bbox,
            providers_id=providers_id,
            countries_id=countries_id,
            parameters_id=parameters_id,
            licenses_id=licenses_id,
            iso=iso,
            monitor=monitor,
            mobile=mobile,
            order_by=order_by,
            sort_order=sort_order,
        )

        locations = await self._client._get("/locations", params=params)
        return LocationsResponse.read_response(locations)

    async def sensors(self, locations_id: int) -> SensorsResponse:
        """Retrieve sensors from a location.

        Args:
            locations_id: The locations ID of the location to retrieve.

        Returns:
            SensorsResponse: An instance representing the retrieved latest results.

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
        sensors = await self._client._get(f"/locations/{locations_id}/sensors")
        return SensorsResponse.read_response(sensors)
