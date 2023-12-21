from __future__ import annotations

from typing import List, Tuple, Union

from openaq.shared.models import build_query_params
from openaq.shared.responses import LocationsResponse

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
            NotAuthorized: Raised for HTTP 401 error, indicating the client is not authorized.
            Forbidden: Raised for HTTP 403 error, indicating the request is forbidden.
            NotFoundError: Raised for HTTP 404 error, indicating a resource is not found.
            ValidationError: Raised for HTTP 422 error, indicating invalid request parameters.
            RateLimit: Raised for HTTP 429 error, indicating rate limit exceeded.
            ServerError: Raised for HTTP 500 error, indicating an internal server error or unexpected server-side issue.
            GatewayTimeoutError: Raised for HTTP 504 error, indicating a gateway timeout.
        """
        location = await self._client._get(f"/locations/{locations_id}")
        return LocationsResponse.load(location.json())

    async def list(
        self,
        page: int = 1,
        limit: int = 1000,
        radius: Union[int, None] = None,
        coordinates: Union[Tuple[float, float], None] = None,
        bbox: Union[Tuple[float, float, float, float], None] = None,
        providers_id: Union[int, List[int], None] = None,
        countries_id: Union[int, List[int], None] = None,
        parameters_id: Union[int, List[int], None] = None,
        iso: Union[str, None] = None,
        monitor: Union[bool, None] = None,
        mobile: Union[bool, None] = None,
        order_by: Union[str, None] = None,
        sort_order: Union[str, None] = None,
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
            iso:  2 letter ISO 3166-alpha-2 country code.
            monitor: Boolean for reference grade monitors (true) or air sensors (false)
            mobile: Boolean mobile locations (true) or not mobile locations (false).
            order_by: Order by operators for results.
            sort_order: Sort order (asc/desc).

        Returns:
            LocationsResponse: An instance representing the list of retrieved locations.

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
            radius=radius,
            coordinates=coordinates,
            bbox=bbox,
            providers_id=providers_id,
            countries_id=countries_id,
            parameters_id=parameters_id,
            iso=iso,
            monitor=monitor,
            mobile=mobile,
            order_by=order_by,
            sort_order=sort_order,
        )

        locations = await self._client._get("/locations", params=params)
        return LocationsResponse.load(locations.json())
