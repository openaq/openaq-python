import datetime

from openaq.shared.models import build_measurements_path, build_query_params
from openaq.shared.responses import MeasurementsResponse
from openaq.shared.types import Data, Rollup
from openaq.shared.validators import (
    validate_data_rollup_compatibility,
    validate_datetime_params,
    validate_integer_id,
    validate_limit_param,
    validate_page_param,
)

from .base import SyncResourceBase


class Measurements(SyncResourceBase):
    """Provides methods to retrieve the measurements resource from the OpenAQ API."""

    def list(
        self,
        sensors_id: int,
        data: Data | None = None,
        rollup: Rollup | None = None,
        datetime_from: datetime.datetime | str | None = "2016-10-10",
        datetime_to: datetime.datetime | str | None = None,
        page: int = 1,
        limit: int = 1000,
    ) -> MeasurementsResponse:
        """List air quality measurements based on provided filters.

        Args:
            sensors_id: The ID of the sensor for which measurements should be retrieved.
            data: The base measurement unit to query
            rollup: The period by which to rollup the base measurement data.
            datetime_from: Starting date for the measurement retrieval. Can be a datetime object or ISO-8601 formatted date or datetime string.
            datetime_to: Ending date for the measurement retrieval. Can be a datetime object or ISO-8601 formatted date or datetime string.
            page: The page number, must be greater than zero. Page count is measurements found / limit.
            limit: The number of results returned per page. Must be between 1 and 1,000.

        Returns:
            MeasurementsResponse: An instance representing the list of retrieved air quality measurements.

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
        sensors_id = validate_integer_id(sensors_id)
        page = validate_page_param(page)
        limit = validate_limit_param(limit)

        data, rollup = validate_data_rollup_compatibility(data, rollup)
        datetime_from, datetime_to = validate_datetime_params(
            datetime_from, datetime_to
        )
        params = build_query_params(
            page=page,
            limit=limit,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
        )
        path = build_measurements_path(sensors_id, data, rollup)

        measurements_response = self._client._get(path, params=params)

        return MeasurementsResponse.read_response(measurements_response)
