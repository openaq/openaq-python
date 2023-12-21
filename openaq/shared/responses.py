"""Response models to represent the resources returned from the OpenAQ API."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from types import ModuleType
from typing import Any, Dict, List, Tuple, Union

from openaq.utils.humps import camelize, decamelize

try:
    import orjson
except ImportError:
    orjson = None


class _ResponseBase:
    """Base clase for all reponse classes.

    Handles serialization and deserialization of JSON data and setting of
    class attributes
    """

    @classmethod
    def _deserialize(cls, data: Mapping):
        """Deserializes data and convert keys from camel case to snake case.

        Args:
            data: input dictionary of API response data to be deserialized.
        """
        out = {}
        for k, v in data.items():
            if isinstance(v, dict):
                out[decamelize(k)] = cls._deserialize(v)
            if isinstance(v, list):
                out[decamelize(k)] = []
                for x in v:
                    if isinstance(x, dict):
                        out[decamelize(k)].append(cls._deserialize(x))
                    else:
                        out[decamelize(k)].append(x)
            else:
                out[decamelize(k)] = v
        return out

    def _serialize(self, data: Mapping):
        """Serializes data and convert keys to camel case.

        Args:
            data: input dictionary of API response data to be serialized.
        """
        if isinstance(data, list):
            return [
                self._serialize(i) if isinstance(i, (Mapping, list)) else i
                for i in data
            ]
        return {
            camelize(k): self._serialize(v) if isinstance(v, (Mapping, list)) else v
            for k, v in data.items()
        }

    @classmethod
    def load(cls, data: Mapping) -> _ResponseBase:
        """Deserializes JSON response from API into response object.

        Args:
            data: A dictionary representation of the data returned from the API.

        Returns:
            Deserialized representation of the response data as a Python object.
        """
        return cls(**cls._deserialize(data))

    def dict(self) -> Dict:
        """Serializes response data to Python dictionary.

        Returns:
            Python dictionary of the response data.
        """
        return asdict(self)

    def json(self, encoder: ModuleType = json) -> str:
        """Serializes response data to JSON string.

        Allows for setting encoder module. Defaults to python core `json`, `orjson` also supported with optional install `pip install openaq[orjson]`

        Args:
            encoder: JSON serializer module.

        Returns:
            string representation of the response in JSON.
        """
        if encoder == orjson:
            assert orjson is not None, "orjson must be installed."
        return encoder.dumps(self._serialize(self.dict()), ensure_ascii=False)


@dataclass
class OpenAQResponse(_ResponseBase):
    """Base class for generic OpenAQ API response.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of records, typed as Any to be overridden.
    """

    meta: Meta
    results: List[Any]


@dataclass
class Meta(_ResponseBase):
    """API response metadata.

    Attributes:
        name: API name
        website: API URL
        page: the page number for paginated results.
        limit: the limit number of records per page.
        found: a count of the total number of records.
    """

    name: str
    website: str
    page: int
    limit: int
    found: int


@dataclass
class CountryBase(_ResponseBase):
    """Base representation for country resource in OpenAQ.

    Attributes:
        id: unique identifier for country
        code: ISO 3166-1 alpha-2 2 letter country code
        name: country name
    """

    id: int
    code: str
    name: str


@dataclass
class InstrumentBase(_ResponseBase):
    """Base representation for instrument resource in OpenAQ.

    Attributes:
        id: unique identifier for instrument
        name: instrument name
    """

    id: int
    name: str


@dataclass
class ManufacturerBase(_ResponseBase):
    """Base representation for manufacturer resource in OpenAQ.

    Attributes:
        id: unique identifier for manufacturer
        name: manufacturer name
    """

    id: int
    name: str


@dataclass
class OwnerBase(_ResponseBase):
    """Base representation for owner resource in OpenAQ.

    Attributes:
        id: unique identifier for owner
        name: owner name
    """

    id: int
    name: str


@dataclass
class ParameterBase(_ResponseBase):
    """Base representation for measurement parameter resource in OpenAQ.

    Attributes:
        id: unique identifier for parameter
        name: parameter name
    """

    id: int
    name: str
    units: str
    display_name: Union[str, None]


@dataclass
class ProviderBase(_ResponseBase):
    """Base representation for providers in OpenAQ.

    Attributes:
        id: unique identifier for provider
        name: provider name
    """

    id: int
    name: str


@dataclass
class SensorBase(_ResponseBase):
    """Base representation for sensor resource in OpenAQ.

    Attributes:
        id: unique identifier for sensor
        name: sensor name
        parameter: parameter measured by sensor
    """

    id: int
    name: str
    parameter: ParameterBase

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.parameter, dict):
            self.parameter = ParameterBase.load(self.parameter)


@dataclass
class Coordinates(_ResponseBase):
    """Representation for geographic coordinates in OpenAQ.

    coordinates are represented in WGS84 (AKA EPSG 4326) coordinate system.

    Attributes:
        latitude: WGS84 latitude coordinate value
        longitude: WGS84 longitude coordinate value
    """

    latitude: float
    longitude: float


@dataclass
class Datetime(_ResponseBase):
    """Representation for timestamps in OpenAQ.

    Attributes:
        utc: ISO-8601 formatted datetime value at UTC
        local: ISO-8601 formatted datetime value at local timezone offset
    """

    utc: str
    local: str


@dataclass
class Location(_ResponseBase):
    """Representation of location resource in OpenAQ.

    Attributes:
        id: unique location identifier
        name: location name
        locality: name of locality
        timezone: timezone of location
        country: country base object with country information
        owner: owner object
        provider: provider object
        is_mobile: boolean indicating whether or not location is mobile (true) or stationary (false)
        is_monitor: boolean indicating whether or not location is a reference monitor (true) or air sensor (false)
        instruments: list of instruments used by locaiton node
        sensors: list of sensors used by location node
        coordinates: coordinates objects with latitude and longitude of location
        bounds: WGS84 geographic bounds of location
        distance: distance from `coordinates` value when querying by radius and coordinates
        datetime_first: ISO 8601 datetime of first measurement for location
        datetime_last: ISO 8601 datetime of last measurement for location

    """

    id: int
    name: str
    locality: Union[str, None]
    timezone: str
    country: CountryBase
    owner: OwnerBase
    provider: ProviderBase
    is_mobile: bool
    is_monitor: bool
    instruments: List[InstrumentBase]
    sensors: List[SensorBase]
    coordinates: Coordinates
    bounds: Tuple[float, float, float, float]
    distance: Union[float, None]
    datetime_first: Datetime
    datetime_last: Datetime

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.country, dict):
            self.country = CountryBase.load(self.country)
        if isinstance(self.owner, dict):
            self.owner = OwnerBase.load(self.owner)
        if isinstance(self.provider, dict):
            self.provider = ProviderBase.load(self.provider)
        if isinstance(self.instruments, list):
            self.instruments = [InstrumentBase.load(x) for x in self.instruments]
        if isinstance(self.sensors, list):
            self.sensors = [SensorBase.load(x) for x in self.sensors]
        if isinstance(self.coordinates, dict):
            self.coordinates = Coordinates.load(self.coordinates)
        if isinstance(self.datetime_first, dict):
            self.datetime_first = Datetime.load(self.datetime_first)
        if isinstance(self.datetime_last, dict):
            self.datetime_last = Datetime.load(self.datetime_last)


@dataclass
class LocationsResponse(_ResponseBase):
    """Representation of the API response for locations resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of location records.

    """

    meta: Meta
    results: List[Location]

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.meta, dict):
            self.meta = Meta.load(self.meta)
        if isinstance(self.results, list):
            self.results = [Location.load(x) for x in self.results]


# Providers


@dataclass
class OwnerEntity(_ResponseBase):
    """Representation of owner entitiy resource in OpenAQ.

    Attributes:
        id: unique identifier for owner entity
        name: owner entity name
    """

    id: int
    name: str


@dataclass
class Bbox(_ResponseBase):
    """Bounding box representation for geographic areas.

    Attributes:
        type: geometry type
        coordinates: list of WGS 84 coordinates of bounding box
    """

    type: str
    coordinates: Union[
        List[List[Tuple[float, float]]], List[Tuple[float, float]], Tuple[float, float]
    ]


@dataclass
class Provider(_ResponseBase):
    """Representation of provider resource in OpenAQ.

    id: unique identifier for provider
    name: provider name
    source_name: name of source
    export_prefix:
    license: data license of provider
    datetime_added: ISO-8601 datetime of when provider was added to OpenAQ
    datetime_first: ISO-8601 datetime of first measurement
    datetime_last: ISO-8601 datetime of first measurement
    owner_entity: owner entity object
    parameters: list of parameters available from provider
    bbox: bounding box of geographic area of provider locations
    """

    id: int
    name: str
    source_name: str
    export_prefix: str
    license: Any
    datetime_added: str
    datetime_first: str
    datetime_last: str
    owner_entity: OwnerEntity
    parameters: List[ParameterBase]
    bbox: Union[Bbox, None]

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.owner_entity, dict):
            self.owner_entity = OwnerEntity.load(self.owner_entity)
        if isinstance(self.parameters, list):
            self.parameters = [ParameterBase.load(x) for x in self.parameters]
        if isinstance(self.bbox, dict):
            self.bbox = Bbox.load(self.bbox)


@dataclass
class ProvidersResponse(_ResponseBase):
    """Representation of the API response for providers resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of provider records.
    """

    meta: Meta
    results: List[Provider]

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.meta, dict):
            self.meta = Meta.load(self.meta)
        if isinstance(self.results, list):
            self.results = [Provider.load(x) for x in self.results]


# Parameters


@dataclass
class Parameter(_ResponseBase):
    """Representation of parameter resource in OpenAQ.

    Attributes:
        id: unique identifier for parameter
        name: name of parameter
        units: units of measurement of parameter
        display_name: display name of parameter
        description: description of parameter
    """

    id: int
    name: str
    units: str
    display_name: Union[str, None] = None
    description: Union[str, None] = None


@dataclass
class ParametersResponse(_ResponseBase):
    """Representation of the API response for parameters resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of parameter records.
    """

    meta: Meta
    results: List[Parameter]

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.meta, dict):
            self.meta = Meta.load(self.meta)
        if isinstance(self.results, list):
            self.results = [Parameter.load(x) for x in self.results]


# Countries


@dataclass
class Country(_ResponseBase):
    """Representation of country resource in OpenAQ.

    Attributes:
        id: unique identifier for country
        code: ISO 3166-1 alpha-2 2 letter country code
        name: name of country
        datetime_first: datetime of first measurement available.
        datetime_last: datetime of last measurement available.
        parameters: list of parameters available in the country.
    """

    id: int
    code: str
    name: str
    datetime_first: str
    datetime_last: str
    parameters: List[ParameterBase]

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.parameters, list):
            self.parameters = [ParameterBase.load(x) for x in self.parameters]


@dataclass
class CountriesResponse(_ResponseBase):
    """Representation of the API response for countries resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of country records.
    """

    meta: Meta
    results: List[Country]

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.meta, dict):
            self.meta = Meta.load(self.meta)
        if isinstance(self.results, list):
            self.results = [Country.load(x) for x in self.results]


# Instruments


@dataclass
class Instrument(_ResponseBase):
    """Representation of instrument resource in OpenAQ.

    Attributes:
        id: unique identifier for instrument
        name: name of instrument
        is_monitor: boolean indicating if instrument is graded as reference monitor.
        manufacturer: instrument manufacturer
    """

    id: int
    name: str
    is_monitor: bool
    manufacturer: ManufacturerBase

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.manufacturer, dict):
            self.manufacturer = ManufacturerBase.load(self.manufacturer)


@dataclass
class InstrumentsResponse(_ResponseBase):
    """Representation of the API response for instruments resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of instrument records.
    """

    meta: Meta
    results: List[Instrument]

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.meta, dict):
            self.meta = Meta.load(self.meta)
        if isinstance(self.results, list):
            self.results = [Instrument.load(x) for x in self.results]


# Manufacturers


@dataclass
class Manufacturer(_ResponseBase):
    """Representation of manufacturer resource in OpenAQ.

    Attributes:
        id: unique identifier for manufacturer
        name: manufacturer name
        instruments: a list of instruments made by the manufacturer
    """

    id: int
    name: str
    instruments: List[InstrumentBase]

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.instruments, list):
            self.instruments = [InstrumentBase.load(x) for x in self.instruments]


@dataclass
class ManufacturersResponse(_ResponseBase):
    """Representation of the API response for manufacturers resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of manufacturer records.
    """

    meta: Meta
    results: List[Manufacturer]

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.meta, dict):
            self.meta = Meta.load(self.meta)
        if isinstance(self.results, list):
            self.results = [Manufacturer.load(x) for x in self.results]


# Measurements


@dataclass
class Summary(_ResponseBase):
    """Statistical summary of measurement values.

    Attributes:
        min: mininum value
        q02: 2nd percentile
        q25: 25th percentile
        median: median value i.e. 50th percentile
        q75: 75th percentile
        q98: 98th percentile
        max: maximum value
        sd: standard deviation
    """

    min: float
    q02: float
    q25: float
    median: float
    q75: float
    q98: float
    max: float
    sd: float


@dataclass
class Coverage(_ResponseBase):
    """Data coverage details for measurements.

    Attributes:
        expected_count:
        expected_interval:
        observed_count:
        observed_interval:
        percent_complete:
        percent_coverage:
        datetime_from:
        datetime_to:
    """

    expected_count: int
    expected_interval: str
    observed_count: int
    observed_interval: str
    percent_complete: float
    percent_coverage: float
    datetime_from: Datetime
    datetime_to: Datetime

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.datetime_from, dict):
            self.datetime_from = Datetime.load(self.datetime_from)
        if isinstance(self.datetime_to, dict):
            self.datetime_to = Datetime.load(self.datetime_to)


@dataclass
class Period(_ResponseBase):
    """Representation of a measurement time period.

    Attributes:
        label: label of measurement period
        interval: time interval of measurement aggregation
        datetime_from: datetime object of period start
        datetime_to: datetime object of period end

    """

    label: str
    interval: str
    datetime_from: Datetime
    datetime_to: Datetime

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.datetime_from, dict):
            self.datetime_from = Datetime.load(self.datetime_from)
        if isinstance(self.datetime_to, dict):
            self.datetime_to = Datetime.load(self.datetime_to)


@dataclass
class Measurement(_ResponseBase):
    """Representation of measurement resource in OpenAQ.

    Attributes:
        period: period object
        value: measured value or mean value if aggregate to period.
        parameter: parameter object
        coordinates: WGS84 coordinate values if location is mobile.
        summary: summary object
        coverage: coverage object
    """

    period: Period
    value: float
    parameter: ParameterBase
    coordinates: Union[Coordinates, None]
    summary: Summary
    coverage: Coverage

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.period, dict):
            self.period = Period.load(self.period)
        if isinstance(self.parameter, dict):
            self.parameter = ParameterBase.load(self.parameter)
        if isinstance(self.coordinates, dict):
            self.coordinates = Coordinates.load(self.coordinates)
        if isinstance(self.summary, dict):
            self.summary = Summary.load(self.summary)
        if isinstance(self.coverage, dict):
            self.coverage = Coverage.load(self.coverage)


@dataclass
class MeasurementsResponse(_ResponseBase):
    """Representation of the API response for measurements resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of measurement records.
    """

    meta: Meta
    results: List[Measurement]

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.meta, dict):
            self.meta = Meta.load(self.meta)
        if isinstance(self.results, list):
            self.results = [Measurement.load(x) for x in self.results]


# Owners


@dataclass
class Owner(_ResponseBase):
    """Detailed information about an owner in OpenAQ.

    Attributes:
        id: unique identifier for owner
        name: owner name
    """

    id: int
    name: str


@dataclass
class OwnersResponse(_ResponseBase):
    """Representation of the API response for owners resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of owner records.
    """

    meta: Meta
    results: List[Owner]

    def __post_init__(self):
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.meta, dict):
            self.meta = Meta.load(self.meta)
        if isinstance(self.results, list):
            self.results = [Owner.load(x) for x in self.results]
