from __future__ import annotations

from typing import Any, Mapping, Union

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
    DEFAULT_USER_AGENT,
    DEFAULT_BASE_URL,
    BaseClient,
)

from .transport import Transport


class OpenAQ(BaseClient):
    """OpenAQ syncronous client.

    Args:
        api_key: The API key for accessing the service.
        user_agent: The user agent string to be used in requests.
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
        NotAuthorized: Raised for HTTP 401 error, indicating the client is not authorized.
        Forbidden: Raised for HTTP 403 error, indicating the request is forbidden.
        NotFoundError: Raised for HTTP 404 error, indicating a resource is not found.
        ValidationError: Raised for HTTP 422 error, indicating invalid request parameters.
        RateLimit: Raised for HTTP 429 error, indicating rate limit exceeded.
        ServerError: Raised for HTTP 500 error, indicating an internal server error or unexpected server-side issue.
        GatewayTimeoutError: Raised for HTTP 504 error, indicating a gateway timeout.

    """

    def __init__(
        self,
        api_key: Union[str, None] = None,
        headers: Mapping[str, str] = {},
        base_url: str = DEFAULT_BASE_URL,
        user_agent: str = DEFAULT_USER_AGENT,
        _transport: Transport = Transport(),
    ) -> OpenAQ:
        super().__init__(_transport, user_agent, headers, api_key, base_url)

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
        params: Union[Mapping[str, Any], None] = None,
        headers: Union[Mapping[str, str], None] = None,
    ):
        request_headers = self.build_request_headers(headers)
        try:
            url = self._base_url + path
            data = self.transport.send_request(
                method=method, url=url, params=params, headers=request_headers
            )
            return data
        except Exception as e:
            raise e

    def _get(
        self,
        path: str,
        *,
        params: Union[Mapping[str, str], None] = None,
        headers: Union[Mapping[str, Any], None] = None,
    ):
        return self._do("get", path, params=params, headers=headers)

    def close(self):
        self._transport.close()

    def __enter__(self) -> OpenAQ:
        return self

    def __exit__(self, *_: Any):
        self.close()
