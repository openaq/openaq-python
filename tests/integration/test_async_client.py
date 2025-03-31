import asyncio
import os

import pytest

from openaq._async.client import AsyncOpenAQ


@pytest.fixture(scope="session")
def event_loop(request):
    """
    Redefine the event loop to support session/module-scoped fixtures;
    see https://github.com/pytest-dev/pytest-asyncio/issues/68
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()

    try:
        yield loop
    finally:
        loop.close()


@pytest.mark.asyncio(scope="class")
class TestAsyncClient:
    loop: asyncio.AbstractEventLoop

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = AsyncOpenAQ(base_url=os.environ.get("TEST_BASE_URL"))

    async def test_locations_list(self):
        await self.client.locations.list()

    async def test_locations_get(self):
        await self.client.locations.get(1)

    async def test_latest_get(self):
        await self.client.locations.latest(1)

    async def test_countries_list(self):
        await self.client.countries.list()

    async def test_countries_get(self):
        await self.client.countries.get(1)

    async def test_licenses_list(self):
        await self.client.licenses.list()

    async def test_licenses_get(self):
        await self.client.licenses.get(1)

    async def test_owners_list(self):
        await self.client.owners.list()

    async def test_owners_get(self):
        await self.client.owners.get(1)

    async def test_parameters_list(self):
        await self.client.parameters.list()

    async def test_parameters_get(self):
        await self.client.parameters.get(1)

    async def test_parameters_latest(self):
        await self.client.parameters.latest(1)

    async def test_providers_list(self):
        await self.client.providers.list()

    async def test_providers_get(self):
        await self.client.providers.get(1)

    async def test_instruments_list(self):
        await self.client.instruments.list()

    async def test_instruments_get(self):
        await self.client.instruments.get(1)

    async def test_manufacturers_list(self):
        await self.client.manufacturers.list()

    async def test_manufacturers_get(self):
        await self.client.manufacturers.get(1)

    async def test_manufacturers_instruments(self):
        await self.client.manufacturers.instruments(1)

    async def test_sensors_get(self):
        await self.client.sensors.get(1)
