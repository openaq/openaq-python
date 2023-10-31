from openaq.shared.models import build_query_params
from openaq.shared.responses import OwnersResponse

from .base import AsyncResourceBase


class Owners(AsyncResourceBase):
    """This provides methods to retrieve owner data from the OpenAQ API."""

    async def get(self, owners_id: int) -> OwnersResponse:
        """Retrieve specific owner data by its owners ID.

        Args:
            owners_id: The owners ID of the owner to retrieve.

        Returns:
            OwnersResponse: An instance representing the retrieved owner.

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
        owner = await self._client._get(f"/owners/{owners_id}")
        return OwnersResponse.load(owner.json())

    async def list(
        self,
        page: int = 1,
        limit: int = 1000,
        order_by: str = None,
        sort_order: str = None,
    ) -> OwnersResponse:
        """List owners based on provided filters.

        Provides the ability to filter the owners resource by the given arguments.

        * `page` - Specifies the page number of results to retrieve
        * `limit` - Sets the number of results generated per page
        * `order_by` - Determines the fields by which results are sorted; available values are `id`
        * `sort_order` - Works in tandem with `order_by` to specify the direction: either `asc` (ascending) or `desc` (descending)

        Args:
            page: The page number. Page count is owners found / limit.
            limit: The number of results returned per page.
            order_by: Order by operators for results.
            sort_order: Sort order (asc/desc).

        Returns:
            OwnersResponse: An instance representing the list of retrieved owners.

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

        owners = await self._client._get("/owners", params=params)
        return OwnersResponse.load(owners.json())
