from __future__ import annotations

from openaq.shared.models import build_query_params
from openaq.shared.responses import CountriesResponse

from .base import AsyncResourceBase


class Countries(AsyncResourceBase):
    """This provides methods to retrieve country data from the OpenAQ API."""

    async def get(self, countries_id: int) -> CountriesResponse:
        """Retrieve specific country data by its countries ID.

        Args:
            countries_id: The countries ID of the country to retrieve.

        Returns:
            CountriesResponse: An instance representing the retrieved country.

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
        country = await self._client._get(f"/countries/{countries_id}")
        return CountriesResponse.read_response(country)

    async def list(
        self,
        page: int = 1,
        limit: int = 1000,
        order_by: str | None = None,
        sort_order: str | None = None,
        parameters_id: int | None = None,
        providers_id: int | None = None,
    ) -> CountriesResponse:
        """List countries based on provided filters.

        Provides the ability to filter the countries resource by the given arguments.

        * `page` - Specifies the page number of results to retrieve
        * `limit` - Sets the number of results generated per page
        * `providers_id` - Filter results by selected providers ID(s)
        * `parameters_id` - Filters results by selected parameters ID(s)
        * `order_by` - Determines the fields by which results are sorted; available values are `id`
        * `sort_order` - Works in tandem with `order_by` to specify the direction: either `asc` (ascending) or `desc` (descending)

        Args:
            page: The page number. Page count is countries found / limit.
            limit: The number of results returned per page.
            order_by: Order by operators for results.
            sort_order: Sort order (asc/desc).
            parameters_id: Single parameters ID or an array of IDs.
            providers_id: Single providers ID or an array of IDs.

        Returns:
            CountriesResponse: An instance representing the list of retrieved countries.

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
            order_by=order_by,
            sort_order=sort_order,
            parameters_id=parameters_id,
            providers_id=providers_id,
        )

        countries = await self._client._get("/countries", params=params)
        return CountriesResponse.read_response(countries)
