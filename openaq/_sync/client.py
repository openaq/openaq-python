from __future__ import annotations

from typing import Any, Mapping

from openaq._sync.models.countries import Countries
from openaq._sync.models.instruments import Instruments
from openaq._sync.models.licenses import Licenses
from openaq._sync.models.locations import Locations
from openaq._sync.models.manufacturers import Manufacturers
from openaq._sync.models.measurements import Measurements
from openaq._sync.models.owners import Owners
from openaq._sync.models.parameters import Parameters
from openaq._sync.models.providers import Providers
from openaq._sync.models.sensors import Sensors
from openaq.shared.client import (
    DEFAULT_BASE_URL,
    BaseClient,
)
from openaq.shared.exceptions import RateLimitError

from .transport import Transport


class OpenAQ(BaseClient[Transport]):
    """OpenAQ syncronous client.

    Args:
        api_key: The API key for accessing the service.
        headers: Additional headers to be sent with the request.
        base_url: The base URL for the API endpoint.

    Note:
        An API key can either be passed directly to the OpenAQ client class at
        instantiation or can be accessed from a system environment variable
        name `OPENAQ-API-KEY`. An API key added at instantiation will always
        override one set in the environment variable.

    Warning:
        Although the `api_key` parameter is not required for instantiating the
        OpenAQ client, an API Key is required for using the OpenAQ API.

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

    def __init__(
        self,
        api_key: str | None = None,
        headers: Mapping[str, str] = {},
        base_url: str = DEFAULT_BASE_URL,
        _transport: Transport = Transport(),
    ) -> None:
        super().__init__(_transport, headers, api_key, base_url)

        self.countries = Countries(self)
        self.instruments = Instruments(self)
        self.licenses = Licenses(self)
        self.locations = Locations(self)
        self.manufacturers = Manufacturers(self)
        self.measurements = Measurements(self)
        self.owners = Owners(self)
        self.providers = Providers(self)
        self.parameters = Parameters(self)
        self.sensors = Sensors(self)

    @property
    def transport(self) -> Transport:
        return self._transport

    def _do(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ):
        self._check_rate_limit()
        request_headers = self.build_request_headers(headers)
        url = self._base_url + path
        data = self.transport.send_request(
            method=method, url=url, params=params, headers=request_headers
        )
        self._set_rate_limit(data.headers)
        return data

    def _get(
        self,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, Any] | None = None,
    ):
        return self._do("get", path, params=params, headers=headers)

    def close(self):
        self._transport.close()

    def __enter__(self) -> OpenAQ:
        return self

    def __exit__(self, *_: Any):
        self.close()
