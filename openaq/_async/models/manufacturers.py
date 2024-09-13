from openaq.shared.models import build_query_params
from openaq.shared.responses import InstrumentsResponse, ManufacturersResponse

from .base import AsyncResourceBase


class Manufacturers(AsyncResourceBase):
    """This provides methods to retrieve manufacturer data from the OpenAQ API."""

    async def get(self, manufacturers_id: int) -> ManufacturersResponse:
        """Retrieve specific manufacturer data by its manufacturers ID.

        Args:
            manufacturers_id: The manufacturers ID of the manufacturer to retrieve.

        Returns:
            ManufacturersResponse: An instance representing the retrieved manufacturer.

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
        manufacturer = await self._client._get(f"/manufacturers/{manufacturers_id}")
        return ManufacturersResponse.read_response(manufacturer)

    async def list(
        self,
        page: int = 1,
        limit: int = 1000,
        order_by: str = None,
        sort_order: str = None,
    ) -> ManufacturersResponse:
        """List manufacturers based on provided filters.

        Provides the ability to filter the manufacturers resource by the given arguments.

        * `page` - Specifies the page number of results to retrieve
        * `limit` - Sets the number of results generated per page
        * `order_by` - Determines the fields by which results are sorted; available values are `id`
        * `sort_order` - Works in tandem with `order_by` to specify the direction: either `asc` (ascending) or `desc` (descending)

        Args:
            page: The page number. Page count is manufacturers found / limit.
            limit: The number of results returned per page.
            order_by: Order by operators for results.
            sort_order: Sort order (asc/desc).

        Returns:
            ManufacturersResponse: An instance representing the list of retrieved manufacturers.

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
            page=page, limit=limit, order_by=order_by, sort_order=sort_order
        )

        manufacturers = await self._client._get("/manufacturers", params=params)
        return ManufacturersResponse.read_response(manufacturers)

    async def instruments(self, manufacturers_id: int) -> InstrumentsResponse:
        """Retrieve instruments of a manufacturer by ID.

        Args:
            manufacturers_id: The manufacturers ID of the manufacturer to retrieve.

        Returns:
            InstrumentsResponse: An instance representing the retrieved instruments.

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
        instruments_response = await self._client._get(
            f"/manufacturers/{manufacturers_id}/instruments"
        )
        return InstrumentsResponse.read_response(instruments_response)
