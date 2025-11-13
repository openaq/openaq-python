from openaq.shared.models import build_query_params
from openaq.shared.responses import ProvidersResponse
from openaq.shared.types import SortOrder
from openaq.shared.validators import (
    validate_geospatial_params,
    validate_integer_id,
    validate_integer_or_list_integer_params,
    validate_iso_param,
    validate_limit_param,
    validate_order_by,
    validate_page_param,
    validate_sort_order,
)

from .base import AsyncResourceBase


class Providers(AsyncResourceBase):
    """This provides methods to retrieve provider data from the OpenAQ API."""

    async def get(self, providers_id: int) -> ProvidersResponse:
        """Retrieve specific provider data by its providers ID.

        Args:
            providers_id: The providers ID of the provider to retrieve.

        Returns:
            ProvidersResponse: An instance representing the retrieved provider.

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
        providers_id = validate_integer_id(providers_id)
        provider = await self._client._get(f"/providers/{providers_id}")
        return ProvidersResponse.read_response(provider)

    async def list(
        self,
        page: int = 1,
        limit: int = 1000,
        order_by: str | None = None,
        sort_order: SortOrder | None = None,
        parameters_id: int | list[int] | None = None,
        monitor: bool | None = None,
        coordinates: tuple[float, float] | None = None,
        radius: int | None = None,
        bbox: tuple[float, float, float, float] | None = None,
        iso: str | None = None,
        countries_id: int | list[int] | None = None,
    ) -> ProvidersResponse:
        """List providers based on provided filters.

        Args:
            page: The page number, must be greater than zero. Page count is providers found / limit.
            limit: The number of results returned per page. Must be between 1 and 1,000.
            parameters_id: Single parameters ID or an array of IDs.
            monitor: Boolean for reference grade monitors (true) or air sensors (false).
            radius: A distance value in meters to search around the given coordinates value, must be between 1 and 25,000 (25km).
            coordinates: WGS 84 coordinate pair in form latitude, longitude (y,x).
            bbox: Geospatial bounding box of min X, min Y, max X, max Y in WGS 84 coordinates. Limited to four decimals precision.
            iso: 2 letter ISO 3166-alpha-2 country code.
            countries_id: Single countries ID or an array of IDs.
            order_by: Order by operators for results.
            sort_order: Order for sorting results (asc/desc).

        Returns:
            ProvidersResponse: An instance representing the list of retrieved providers.

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
        if countries_id:
            countries_id = validate_integer_or_list_integer_params(
                'countries_id', countries_id
            )
        if parameters_id:
            parameters_id = validate_integer_or_list_integer_params(
                'parameters_id', parameters_id
            )
        if iso:
            iso = validate_iso_param(iso)
        if sort_order:
            sort_order = validate_sort_order(sort_order)
        if order_by:
            order_by = validate_order_by(order_by)
        params = build_query_params(
            page=page,
            limit=limit,
            order_by=order_by,
            sort_order=sort_order,
            parameters_id=parameters_id,
            monitor=monitor,
            coordinates=coordinates,
            radius=radius,
            bbox=bbox,
            iso=iso,
            countries_id=countries_id,
        )

        providers = await self._client._get("/providers", params=params)
        return ProvidersResponse.read_response(providers)
