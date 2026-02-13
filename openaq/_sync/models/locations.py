from openaq.shared.models import build_query_params
from openaq.shared.responses import (
    LatestResponse,
    LocationsResponse,
    SensorsResponse,
)
from openaq.shared.types import SortOrder
from openaq.shared.validators import (
    validate_countries_query_parameters,
    validate_geospatial_params,
    validate_integer_id,
    validate_integer_or_list_integer_params,
    validate_limit_param,
    validate_mobile,
    validate_monitor,
    validate_order_by,
    validate_page_param,
    validate_sort_order,
)

from .base import SyncResourceBase


class Locations(SyncResourceBase):
    """Provides methods to retrieve the locations resource from the OpenAQ API."""

    def get(self, locations_id: int) -> LocationsResponse:
        """Retrieve a specific location by its locations ID.

        Args:
            locations_id: The locations ID of the location to retrieve.

        Returns:
            LocationsResponse: An instance representing the retrieved location.

        Raises:
            IdentifierOutOfBoundsError: Client validation error, identifier outside support int32 range.
            ApiKeyMissingError: Authentication error, missing API Key credentials.
            BadRequestError: Raised for HTTP 400 error, indicating a client request error.
            NotAuthorizedError: Raised for HTTP 401 error, indicating the client is not authorized.
            ForbiddenError: Raised for HTTP 403 error, indicating the request is forbidden.
            NotFoundError: Raised for HTTP 404 error, indicating a resource is not found.
            TimeoutError: Raised for HTTP 408 error, indicating the request has timed out.
            ValidationError: Raised for HTTP 422 error, indicating invalid request parameters.
            RateLimitError: Raised when managed client exceeds rate limit.
            HTTPRateLimitError: Raised for HTTP 429 error, indicating rate limit exceeded.
            ServerError: Raised for HTTP 500 error, indicating an internal server error or unexpected server-side issue.
            BadGatewayError: Raised for HTTP 502, indicating that the gateway or proxy received an invalid response from the upstream server.
            ServiceUnavailableError: Raised for HTTP 503, indicating that the server is not ready to handle the request.
            GatewayTimeoutError: Raised for HTTP 504 error, indicating a gateway timeout.
        """
        locations_id = validate_integer_id(locations_id)
        location_response = self._client._get(f"/locations/{locations_id}")
        return LocationsResponse.read_response(location_response)

    def latest(self, locations_id: int) -> LatestResponse:
        """Retrieve latest measurements from a location.

        Args:
            locations_id: The locations ID of the location to retrieve.

        Returns:
            LatestResponse: An instance representing the retrieved latest results.

        Raises:
            IdentifierOutOfBoundsError: Client validation error, identifier outside support int32 range.
            ApiKeyMissingError: Authentication error, missing API Key credentials.
            BadRequestError: Raised for HTTP 400 error, indicating a client request error.
            NotAuthorizedError: Raised for HTTP 401 error, indicating the client is not authorized.
            ForbiddenError: Raised for HTTP 403 error, indicating the request is forbidden.
            NotFoundError: Raised for HTTP 404 error, indicating a resource is not found.
            TimeoutError: Raised for HTTP 408 error, indicating the request has timed out.
            ValidationError: Raised for HTTP 422 error, indicating invalid request parameters.
            RateLimitError: Raised when managed client exceeds rate limit.
            HTTPRateLimitError: Raised for HTTP 429 error, indicating rate limit exceeded.
            ServerError: Raised for HTTP 500 error, indicating an internal server error or unexpected server-side issue.
            BadGatewayError: Raised for HTTP 502, indicating that the gateway or proxy received an invalid response from the upstream server.
            ServiceUnavailableError: Raised for HTTP 503, indicating that the server is not ready to handle the request.
            GatewayTimeoutError: Raised for HTTP 504 error, indicating a gateway timeout.
        """
        locations_id = validate_integer_id(locations_id)
        latest = self._client._get(f"/locations/{locations_id}/latest")
        return LatestResponse.read_response(latest)

    def list(
        self,
        page: int = 1,
        limit: int = 100,
        radius: int | None = None,
        coordinates: tuple[float, float] | None = None,
        bbox: tuple[float, float, float, float] | None = None,
        providers_id: int | list[int] | None = None,
        countries_id: int | list[int] | None = None,
        parameters_id: int | list[int] | None = None,
        licenses_id: int | list[int] | None = None,
        instruments_id: int | list[int] | None = None,
        manufacturers_id: int | list[int] | None = None,
        owners_id: int | list[int] | None = None,
        iso: str | None = None,
        monitor: bool | None = None,
        mobile: bool | None = None,
        order_by: str | None = None,
        sort_order: SortOrder | None = None,
    ) -> LocationsResponse:
        """List locations based on provided filters.

        Args:
            page: Page number to retrieve, must be greater than zero.
                Page count is calculated as total locations / limit.
            limit: Number of results per page. Must be between 1 and 1,000.
            radius: Search radius in meters around the coordinates point.
                Must be between 1 and 25,000 (25km).
            coordinates: WGS 84 coordinate pair as (latitude, longitude).
            bbox: Geospatial bounding box as (min_x, min_y, max_x, max_y)
                in WGS 84 coordinates. Limited to four decimal places.
            providers_id: Filter locations by provider ID(s).
                Accepts a single ID or list of IDs.
            countries_id: Filter locations by country ID(s).
                Accepts a single ID or list of IDs.
            parameters_id: Filter locations by parameter ID(s).
                Accepts a single ID or list of IDs.
            licenses_id: Filter locations by license ID(s).
                Accepts a single ID or list of IDs.
            instruments_id: Filter locations by instrument ID(s).
                Accepts a single ID or list of IDs.
            manufacturers_id: Filter locations by manufacturer ID(s).
                Accepts a single ID or list of IDs.
            owners_id: Filter locations by owner ID(s).
                Accepts a single ID or list of IDs.
            iso: Filter locations by 2-letter ISO 3166-alpha-2 country code.
            monitor: Filter by monitor type. True for reference grade monitors,
                False for air sensors.
            mobile: Filter by mobility. True for mobile locations,
                False for stationary locations.
            order_by: Field name to sort results by.
            sort_order: Sort direction, either 'asc' or 'desc'.

        Returns:
            LocationsResponse: An instance representing the list of retrieved locations.

        Raises:
            InvalidParameterError: Client validation error, query parameter is not correct type or value.
            IdentifierOutOfBoundsError: Client validation error, identifier outside support int32 range.
            ApiKeyMissingError: Authentication error, missing API Key credentials.
            BadRequestError: Raised for HTTP 400 error, indicating a client request error.
            NotAuthorizedError: Raised for HTTP 401 error, indicating the client is not authorized.
            ForbiddenError: Raised for HTTP 403 error, indicating the request is forbidden.
            NotFoundError: Raised for HTTP 404 error, indicating a resource is not found.
            TimeoutError: Raised for HTTP 408 error, indicating the request has timed out.
            ValidationError: Raised for HTTP 422 error, indicating invalid request parameters.
            RateLimitError: Raised when managed client exceeds rate limit.
            HTTPRateLimitError: Raised for HTTP 429 error, indicating rate limit exceeded.
            ServerError: Raised for HTTP 500 error, indicating an internal server error or unexpected server-side issue.
            BadGatewayError: Raised for HTTP 502, indicating that the gateway or proxy received an invalid response from the upstream server.
            ServiceUnavailableError: Raised for HTTP 503, indicating that the server is not ready to handle the request.
            GatewayTimeoutError: Raised for HTTP 504 error, indicating a gateway timeout.
        """
        page = validate_page_param(page)
        limit = validate_limit_param(limit)
        validate_geospatial_params(coordinates, radius, bbox)
        countries_id, iso = validate_countries_query_parameters(countries_id, iso)
        if providers_id is not None:
            providers_id = validate_integer_or_list_integer_params(
                'providers_id', providers_id
            )
        if parameters_id is not None:
            parameters_id = validate_integer_or_list_integer_params(
                'parameters_id', parameters_id
            )
        if licenses_id is not None:
            licenses_id = validate_integer_or_list_integer_params(
                'licenses_id', licenses_id
            )
        if instruments_id:
            instruments_id = validate_integer_or_list_integer_params(
                'instruments_id', instruments_id
            )
        if manufacturers_id:
            manufacturers_id = validate_integer_or_list_integer_params(
                'manufacturers_id', manufacturers_id
            )
        if owners_id:
            owners_id = validate_integer_or_list_integer_params('owners_id', owners_id)
        if monitor is not None:
            monitor = validate_monitor(monitor)
        if mobile is not None:
            mobile = validate_mobile(mobile)
        if sort_order is not None:
            sort_order = validate_sort_order(sort_order)
        if order_by is not None:
            order_by = validate_order_by(order_by)
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
            instruments_id=instruments_id,
            manufacturers_id=manufacturers_id,
            owner_contacts_id=owners_id,
            iso=iso,
            monitor=monitor,
            mobile=mobile,
            order_by=order_by,
            sort_order=sort_order,
        )

        locations_response = self._client._get("/locations", params=params)
        return LocationsResponse.read_response(locations_response)

    def sensors(self, locations_id: int) -> SensorsResponse:
        """Retrieve sensors from a location.

        Args:
            locations_id: The locations ID of the location to retrieve.

        Returns:
            SensorsResponse: An instance representing the retrieved latest results.

        Raises:
            IdentifierOutOfBoundsError: Client validation error, identifier outside support int32 range.
            ApiKeyMissingError: Authentication error, missing API Key credentials.
            BadRequestError: Raised for HTTP 400 error, indicating a client request error.
            NotAuthorizedError: Raised for HTTP 401 error, indicating the client is not authorized.
            ForbiddenError: Raised for HTTP 403 error, indicating the request is forbidden.
            NotFoundError: Raised for HTTP 404 error, indicating a resource is not found.
            TimeoutError: Raised for HTTP 408 error, indicating the request has timed out.
            ValidationError: Raised for HTTP 422 error, indicating invalid request parameters.
            RateLimitError: Raised when managed client exceeds rate limit.
            HTTPRateLimitError: Raised for HTTP 429 error, indicating rate limit exceeded.
            ServerError: Raised for HTTP 500 error, indicating an internal server error or unexpected server-side issue.
            BadGatewayError: Raised for HTTP 502, indicating that the gateway or proxy received an invalid response from the upstream server.
            ServiceUnavailableError: Raised for HTTP 503, indicating that the server is not ready to handle the request.
            GatewayTimeoutError: Raised for HTTP 504 error, indicating a gateway timeout.
        """
        locations_id = validate_integer_id(locations_id)
        sensors = self._client._get(f"/locations/{locations_id}/sensors")
        return SensorsResponse.read_response(sensors)
