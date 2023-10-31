from __future__ import annotations

from typing import Any, Mapping, Union

from openaq._async.models.countries import Countries
from openaq._async.models.instruments import Instruments
from openaq._async.models.locations import Locations
from openaq._async.models.manufacturers import Manufacturers
from openaq._async.models.measurements import Measurements
from openaq._async.models.owners import Owners
from openaq._async.models.parameters import Parameters
from openaq._async.models.providers import Providers
from openaq.shared.client import (
    DEFAULT_USER_AGENT,
    BaseClient,
    resolve_headers,
)

from .transport import AsyncTransport


class AsyncOpenAQ(BaseClient):
    """OpenAQ asynchronous client.

    Args:
        api_key: The API key for accessing the service.
        user_agent: The user agent string to be used in requests.
        headers: Additional headers to be sent with the request.
        base_url: The base URL for the API endpoint.

    Note:
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
        user_agent: str = DEFAULT_USER_AGENT,
        headers: Mapping[str, str] = {},
        base_url: str = "https://api.openaq.org/v3/",
        _transport: AsyncTransport = AsyncTransport(),
    ) -> AsyncOpenAQ:
        super().__init__(_transport, headers, base_url)
        if headers:
            self._headers.update(headers)
        self._headers = resolve_headers(
            self._headers,
            api_key=api_key,
            user_agent=user_agent,
        )

        self.locations = Locations(self)
        self.providers = Providers(self)
        self.parameters = Parameters(self)
        self.countries = Countries(self)
        self.instruments = Instruments(self)
        self.manufacturers = Manufacturers(self)
        self.measurements = Measurements(self)
        self.owners = Owners(self)

    @property
    def transport(self) -> AsyncTransport:
        return self._transport

    async def _do(
        self,
        method: str,
        path: str,
        *,
        params: Union[Mapping[str, Any], None] = None,
        headers: Union[Mapping[str, str], None] = None,
    ):
        if headers:
            request_headers = self._headers.copy()
            request_headers.update(headers)
        else:
            request_headers = self._headers
        try:
            url = self._base_url + path
            data = await self.transport.send_request(
                method=method, url=url, params=params, headers=request_headers
            )
            return data
        except Exception as e:
            raise e

    async def _get(
        self,
        path: str,
        *,
        params: Union[Mapping[str, str], None] = None,
        headers: Union[Mapping[str, Any], None] = None,
    ):
        return await self._do("get", path, params=params, headers=headers)

    async def close(self):
        await self._transport.close()

    async def __aenter__(self) -> AsyncOpenAQ:
        return self

    async def __aexit__(self, *_: Any):
        await self.close()
