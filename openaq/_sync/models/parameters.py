from openaq.shared.models import build_query_params
from openaq.shared.responses import ParametersResponse

from .base import SyncResourceBase


class Parameters(SyncResourceBase):
    """This provides methods to retrieve parameter data from the OpenAQ API."""

    def get(self, parameters_id: int) -> ParametersResponse:
        """Retrieve specific parameter data by its parameters ID.

        Args:
            parameters_id: The parameters ID of the parameter to retrieve.

        Returns:
            ParametersResponse: An instance representing the retrieved parameter.

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
        parameter = self._client._get(f"/parameters/{parameters_id}")
        return ParametersResponse.load(parameter.json())

    def list(
        self,
        page: int = 1,
        limit: int = 1000,
        order_by: str = None,
        sort_order: str = None,
        parameter_type: str = None,
        coordinates: tuple = None,
        radius: int = None,
        bbox: tuple = None,
        iso: str = None,
        countries_id: int = None,
    ) -> ParametersResponse:
        """List parameters based on provided filters.

        Provides the ability to filter the parameters resource by the given arguments.

        * `page` - Specifies the page number of results to retrieve
        * `limit` - Sets the number of results generated per page
        * `parameter_type` - Filters results by type of parameter (pollutant or meteorological)
        * `radius` - Defines the distance around a given point to filter locations within that circular area. Always use with `coordinates` and not with `bbox`
        * `coordinates` - Filters locations by coordinates. Must be used with `radius`, cannot be used in combination with `bbox`
        * `bbox` - Filters locations using a bounding box. Cannot be used with `coordinates` or `radius`
        * `iso` - Filters results by selected country code
        * `countries_id` - Filters results by selected countries ID(s)
        * `order_by` - Determines the fields by which results are sorted; available values are `id`
        * `sort_order` - Works in tandem with `order_by` to specify the direction: either `asc` (ascending) or `desc` (descending)

        Args:
            page: The page number. Page count is parameters found / limit.
            limit: The number of results returned per page.
            parameter_type: pollutant or meteorological.
            radius: A distance value in meters to search around the given coordinates value.
            coordinates: WGS 84 coordinate pair in form latitude, longitude (y,x).
            bbox: Geospatial bounding box of min X, min Y, max X, max Y in WGS 84 coordinates. Limited to four decimals precision.
            iso:  2 letter ISO 3166-alpha-2 country code.
            countries_id: Single countries ID or an array of IDs.
            order_by: Order by operators for results.
            sort_order: Sort order (asc/desc).

        Returns:
            ParametersResponse: An instance representing the list of retrieved parameters.

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
            parameter_type=parameter_type,
            coordinates=coordinates,
            radius=radius,
            bbox=bbox,
            iso=iso,
            countries_id=countries_id,
        )

        parameters = self._client._get("/parameters", params=params)
        return ParametersResponse.load(parameters.json())
