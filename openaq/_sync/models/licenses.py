from openaq.shared.models import build_query_params
from openaq.shared.responses import LicensesResponse
from openaq.shared.types import SortOrder
from openaq.shared.validators import (
    validate_integer_id,
    validate_limit_param,
    validate_order_by,
    validate_page_param,
    validate_sort_order,
)

from .base import SyncResourceBase


class Licenses(SyncResourceBase):
    """Provides methods to retrieve the license resource from the OpenAQ API."""

    def get(self, licenses_id: int) -> LicensesResponse:
        """Retrieve a specific license by its licenses ID.

        Args:
            licenses_id: The licenses ID of the license to retrieve.

        Returns:
            LicensesReponse: An instance representing the retrieved license.

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
        licenses_id = validate_integer_id(licenses_id)
        license = self._client._get(f"/licenses/{licenses_id}")
        return LicensesResponse.read_response(license)

    def list(
        self,
        page: int = 1,
        limit: int = 1000,
        order_by: str | None = None,
        sort_order: SortOrder | None = None,
    ) -> LicensesResponse:
        """List licenses based on provided filters.

        Args:
            page: The page number, must be greater than zero. Page count is licenses found / limit.
            limit: The number of results returned per page. Must be between 1 and 1,000.
            order_by: Order by operators for results.
            sort_order: Order for sorting results (asc/desc).

        Returns:
            LicensesReponse: An instance representing the list of retrieved licenses.

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
        if sort_order is not None:
            sort_order = validate_sort_order(sort_order)
        if order_by is not None:
            order_by = validate_order_by(order_by)
        params = build_query_params(
            page=page,
            limit=limit,
            order_by=order_by,
            sort_order=sort_order,
        )

        licenses = self._client._get("/licenses", params=params)
        return LicensesResponse.read_response(licenses)
