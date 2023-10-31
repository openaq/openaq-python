from openaq.shared.models import build_query_params
from openaq.shared.responses import ProvidersResponse

from .base import SyncResourceBase


class Providers(SyncResourceBase):
    """This provides methods to retrieve provider data from the OpenAQ API."""

    def get(self, providers_id: int) -> ProvidersResponse:
        """Retrieve specific provider data by its providers ID.

        Args:
            providers_id: The providers ID of the provider to retrieve.

        Returns:
            ProvidersResponse: An instance representing the retrieved provider.

        Raises:
            See the 'Raises' section of the 'list' method for potential exceptions.
        """
        provider = self._client._get(f"/providers/{providers_id}")
        return ProvidersResponse.load(provider.json())

    def list(
        self,
        page: int = 1,
        limit: int = 1000,
        order_by: str = None,
        sort_order: str = None,
        parameters_id: int = None,
        monitor: bool = None,
        coordinates: tuple = None,
        radius: int = None,
        bbox: tuple = None,
        iso: str = None,
        countries_id: int = None,
    ) -> ProvidersResponse:
        """List providers based on provided filters.

        Provides the ability to filter the providers resource by the given arguments.

        * `page` - Specifies the page number of results to retrieve
        * `limit` - Sets the number of results generated per page
        * `parameters_id` - Filters results by selected parameters ID(s)
        * `monitor` - Filters results by reference grade monitors (`true`), air sensors (`false`), or both if not used
        * `radius` - Defines the distance around a given point to filter locations within that circular area. Always use with `coordinates` and not with `bbox`
        * `coordinates` - Filters locations by coordinates. Must be used with `radius`, cannot be used in combination with `bbox`
        * `bbox` - Filters locations using a bounding box. Cannot be used with `coordinates` or `radius`
        * `iso` - Filters results by selected country code
        * `countries_id` - Filter results by selected countries ID(s)
        * `order_by` - Determines the fields by which results are sorted; available values are `id`
        * `sort_order` - Works in tandem with `order_by` to specify the direction: either `asc` (ascending) or `desc` (descending)

        Args:
            page: The page number. Page count is providers found / limit.
            limit: The number of results returned per page.
            parameters_id: Single parameters ID or an array of IDs.
            monitor: Boolean for reference grade monitors (true) or air sensors (false).
            radius: A distance value in meters to search around the given coordinates value.
            coordinates: WGS 84 coordinate pair in form latitude, longitude (y,x).
            bbox: Geospatial bounding box of min X, min Y, max X, max Y in WGS 84 coordinates. Limited to four decimals precision.
            iso:  2 letter ISO 3166-alpha-2 country code.
            countries_id: Single countries ID or an array of IDs.
            order_by: Order by operators for results.
            sort_order: Sort order (asc/desc).

        Returns:
            ProvidersResponse: An instance representing the list of retrieved providers.

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

        providers = self._client._get("/providers", params=params)
        return ProvidersResponse.load(providers.json())
