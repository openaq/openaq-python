import os
import pytest

from openaq._sync.client import OpenAQ


class TestClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = OpenAQ(base_url=os.environ.get("TEST_BASE_URL"))

    def test_locations_list(self):
        self.client.locations.list()

    def test_locations_get(self):
        self.client.locations.get(1)

    def test_countries_list(self):
        self.client.countries.list()

    def test_countries_get(self):
        self.client.countries.get(1)

    def test_licenses_list(self):
        self.client.licenses.list()

    def test_licenses_get(self):
        self.client.licenses.get(1)

    def test_owners_list(self):
        self.client.owners.list()

    def test_owners_get(self):
        self.client.owners.get(1)

    def test_parameters_list(self):
        self.client.parameters.list()

    def test_parameters_get(self):
        self.client.parameters.get(1)

    def test_parameters_latest(self):
        self.client.parameters.latest(1)

    def test_providers_list(self):
        self.client.providers.list()

    def test_providers_get(self):
        self.client.providers.get(1)

    def test_instruments_list(self):
        self.client.instruments.list()

    def test_instruments_get(self):
        self.client.instruments.get(1)

    def test_manufacturers_list(self):
        self.client.manufacturers.list()

    def test_manufacturers_get(self):
        self.client.manufacturers.get(1)

    def test_manufacturers_instruments(self):
        self.client.manufacturers.instruments(1)

    def test_sensors_get(self):
        self.client.sensors.get(1)
