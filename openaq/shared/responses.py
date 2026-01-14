"""Response models to represent the resources returned from the OpenAQ API."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, fields
from types import ModuleType
from typing import Any, Generic, TypeVar, cast, get_args

import httpx

from openaq.vendor.humps import camelize, decamelize

try:
    import orjson
except ImportError:
    orjson = None  # type: ignore[assignment]

T = TypeVar("T", bound="_ResourceBase")

_DECAMELIZE_CACHE: dict[str, str] = {}


class _ResourceBase:
    """Base clase for all response classes.

    Handles serialization and deserialization of JSON data and setting of
    class attributes

    """

    __slots__ = ()

    @classmethod
    def _deserialize(cls: type[T], data: Mapping[str, Any]) -> dict[str, Any]:
        """Deserializes data and convert keys from camel case to snake case.

        Args:
            data: input dictionary of API response data to be deserialized.
        """
        out: dict[str, Any] = {}
        for k, v in data.items():
            if k not in _DECAMELIZE_CACHE:
                _DECAMELIZE_CACHE[k] = cast(str, decamelize(k))
            key = _DECAMELIZE_CACHE[k]
            if isinstance(v, dict):
                out[key] = cls._deserialize(v)
            elif isinstance(v, list):
                out[key] = [
                    cls._deserialize(x) if isinstance(x, dict) else x for x in v
                ]
            else:
                out[key] = v
        return out

    @classmethod
    def load(cls: type[T], results: Mapping[str, Any]) -> T:
        """Deserializes JSON response from API into response object.

        Args:
            results: A dictionary representation of the data returned from the API.

        Returns:
            Deserialized representation of the response data as a Python object.
        """
        deserialized_data = cls._deserialize(results)

        # Filter out fields that are not in the class annotations
        expected_fields = {
            k: v for k, v in deserialized_data.items() if k in cls.__annotations__
        }
        return cls(**expected_fields)


@dataclass(slots=True)
class Headers:
    """API response headers.

    Attributes:
        x_ratelimit_limit: The X-RateLimit-Limit header indicates the maximum number of requests for rate limit policy
        x_ratelimit_remaining: The X-RateLimit-Remaining header indicates the remaining number of requests for the period
        x_ratelimit_used: The X-RateLimit-Remaining header indicates the number of requests used for the period
        x_ratelimit_reset: The X-RateLimit-Reset header indicates when, in number of seconds, the rate limit period resets
    """

    x_ratelimit_limit: int | None = None
    x_ratelimit_remaining: int | None = None
    x_ratelimit_used: int | None = None
    x_ratelimit_reset: int | None = None

    def __post_init__(self) -> None:
        """Coerces attribute values to correct types."""
        self.x_ratelimit_limit = int(self.x_ratelimit_limit or 0)
        self.x_ratelimit_remaining = int(self.x_ratelimit_remaining or 0)
        self.x_ratelimit_used = int(self.x_ratelimit_used or 0)
        self.x_ratelimit_reset = int(self.x_ratelimit_reset or 0)


@dataclass(slots=True)
class Meta(_ResourceBase):
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


R = TypeVar("R", bound="_ResponseBase")

TResult = TypeVar("TResult")


@dataclass(slots=True)
class _ResponseBase(Generic[TResult]):
    """Base clase for all response classes.

    Handles serialization and deserialization of JSON data and setting of
    class attributes

    Attributes:
        headers:
        meta:
    """

    headers: Headers
    meta: Meta
    results: list[TResult]

    @classmethod
    def read_response(cls: type[R], response: httpx.Response) -> R:
        valid_headers = [field.name for field in fields(Headers)]
        json_data = response.json()
        return cls(
            Headers(
                **{
                    k.replace('-', '_'): int(v) if v.isdigit() else None
                    for k, v in response.headers.items()
                    if k.replace('-', '_') in valid_headers
                }
            ),
            json_data['meta'],
            json_data['results'],
        )

    def __post_init__(self) -> None:
        """Automatically convert meta and results based on type hints."""
        if isinstance(self.meta, dict):
            self.meta = Meta.load(self.meta)

        if hasattr(self.__class__, '__orig_bases__'):
            for base in self.__class__.__orig_bases__:
                if hasattr(base, '__args__'):
                    result_type = get_args(base)[0]
                    if isinstance(self.results, list) and self.results:
                        if isinstance(self.results[0], dict):
                            self.results = [result_type.load(x) for x in self.results]
                    break

    def _serialize(self, data: Mapping | list) -> dict[str, Any] | list[Any]:
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
            cast(str, camelize(k)): (
                self._serialize(v) if isinstance(v, (Mapping, list)) else v
            )
            for k, v in data.items()
        }

    def dict(self) -> dict:
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


@dataclass(slots=True)
class CountryBase(_ResourceBase):
    """Base representation for country resource in OpenAQ.

    Attributes:
        id: unique identifier for country
        code: ISO 3166-1 alpha-2 2 letter country code
        name: country name
    """

    id: int
    code: str
    name: str


@dataclass(slots=True)
class InstrumentBase(_ResourceBase):
    """Base representation for instrument resource in OpenAQ.

    Attributes:
        id: unique identifier for instrument
        name: instrument name
    """

    id: int
    name: str


@dataclass(slots=True)
class ManufacturerBase(_ResourceBase):
    """Base representation for manufacturer resource in OpenAQ.

    Attributes:
        id: unique identifier for manufacturer
        name: manufacturer name
    """

    id: int
    name: str


@dataclass(slots=True)
class OwnerBase(_ResourceBase):
    """Base representation for owner resource in OpenAQ.

    Attributes:
        id: unique identifier for owner
        name: owner name
    """

    id: int
    name: str


@dataclass(slots=True)
class ParameterBase(_ResourceBase):
    """Base representation for measurement parameter resource in OpenAQ.

    Attributes:
        id: unique identifier for parameter
        name: parameter name
    """

    id: int
    name: str
    units: str
    display_name: str | None


@dataclass(slots=True)
class ProviderBase(_ResourceBase):
    """Base representation for providers in OpenAQ.

    Attributes:
        id: unique identifier for provider
        name: provider name
    """

    id: int
    name: str


@dataclass(slots=True)
class SensorBase(_ResourceBase):
    """Base representation for sensor resource in OpenAQ.

    Attributes:
        id: unique identifier for sensor
        name: sensor name
        parameter: parameter measured by sensor
    """

    id: int
    name: str
    parameter: ParameterBase

    def __post_init__(self) -> None:
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.parameter, dict):
            self.parameter = ParameterBase.load(self.parameter)


@dataclass(slots=True)
class Coordinates(_ResourceBase):
    """Representation for geographic coordinates in OpenAQ.

    coordinates are represented in WGS84 (AKA EPSG 4326) coordinate system.

    Attributes:
        latitude: WGS84 latitude coordinate value
        longitude: WGS84 longitude coordinate value
    """

    latitude: float
    longitude: float


@dataclass(slots=True)
class Datetime(_ResourceBase):
    """Representation for timestamps in OpenAQ.

    Attributes:
        utc: ISO-8601 formatted datetime value at UTC
        local: ISO-8601 formatted datetime value at local timezone offset
    """

    utc: str
    local: str


@dataclass(slots=True)
class Location(_ResourceBase):
    """Representation of location resource in OpenAQ.

    Attributes:
        id: unique location identifier
        name: location name
        locality: name of locality
        timezone: timezone of location
        country: country base object with country information
        owner: object with information about the location owner
        provider: object with information about the location provider
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
    locality: str | None
    timezone: str
    country: CountryBase
    owner: OwnerBase
    provider: ProviderBase
    is_mobile: bool
    is_monitor: bool
    instruments: list[InstrumentBase]
    sensors: list[SensorBase]
    coordinates: Coordinates
    bounds: tuple[float, float, float, float]
    distance: float | None
    datetime_first: Datetime
    datetime_last: Datetime

    def __post_init__(self) -> None:
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.country, dict):
            self.country = CountryBase.load(self.country)
        if isinstance(self.owner, dict):
            self.owner = OwnerBase.load(self.owner)
        if isinstance(self.provider, dict):
            self.provider = ProviderBase.load(self.provider)
        if isinstance(self.instruments, list):
            self.instruments = [
                InstrumentBase.load(x) if isinstance(x, dict) else x
                for x in self.instruments
            ]
        if isinstance(self.sensors, list):
            self.sensors = [
                SensorBase.load(x) if isinstance(x, dict) else x for x in self.sensors
            ]
        if isinstance(self.coordinates, dict):
            self.coordinates = Coordinates.load(self.coordinates)
        if isinstance(self.bounds, list):
            self.bounds = tuple(self.bounds)
        if isinstance(self.datetime_first, dict):
            self.datetime_first = Datetime.load(self.datetime_first)
        if isinstance(self.datetime_last, dict):
            self.datetime_last = Datetime.load(self.datetime_last)


@dataclass(slots=True)
class LocationsResponse(_ResponseBase[Location]):
    """Representation of the API response for locations resource.

    Attributes:
        headers: a Headers object of response headers
        meta: a metadata object containing information about the results.
        results: a list of location records.

    """

    results: list[Location]


# Providers


@dataclass(slots=True)
class OwnerEntity(_ResourceBase):
    """Representation of owner entitiy resource in OpenAQ.

    Attributes:
        id: unique identifier for owner entity
        name: owner entity name
    """

    id: int
    name: str


@dataclass(slots=True)
class Bbox(_ResourceBase):
    """Bounding box representation for geographic areas.

    Attributes:
        type: geometry type
        coordinates: list of WGS 84 coordinates of bounding box
    """

    type: str
    coordinates: (
        list[list[tuple[float, float]]]
        | list[tuple[float, float]]
        | tuple[float, float]
    )


@dataclass(slots=True)
class Provider(_ResourceBase):
    """Representation of provider resource in OpenAQ.

    id: unique identifier for provider
    name: provider name
    source_name: name of source
    export_prefix:
    datetime_added: ISO-8601 datetime of when provider was added to OpenAQ
    datetime_first: ISO-8601 datetime of first measurement
    datetime_last: ISO-8601 datetime of first measurement
    entities_id: entity id
    parameters: list of parameters available from provider
    bbox: bounding box of geographic area of provider locations
    """

    id: int
    name: str
    source_name: str
    export_prefix: str
    datetime_added: str
    datetime_first: str
    datetime_last: str
    entities_id: int
    parameters: list[ParameterBase]
    bbox: Bbox | None

    def __post_init__(self) -> None:
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.parameters, list):
            self.parameters = [
                ParameterBase.load(cast(dict[str, Any], x)) for x in self.parameters
            ]
        if isinstance(self.bbox, dict):
            self.bbox = Bbox.load(self.bbox)


@dataclass(slots=True)
class ProvidersResponse(_ResponseBase[Provider]):
    """Representation of the API response for providers resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of provider records.
    """

    results: list[Provider]


# Parameters


@dataclass(slots=True)
class Parameter(_ResourceBase):
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
    display_name: str | None = None
    description: str | None = None


@dataclass(slots=True)
class ParametersResponse(_ResponseBase[Parameter]):
    """Representation of the API response for parameters resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of parameter records.
    """

    results: list[Parameter]


# Countries


@dataclass(slots=True)
class Country(_ResourceBase):
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
    parameters: list[ParameterBase]

    def __post_init__(self) -> None:
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.parameters, list):
            self.parameters = [
                ParameterBase.load(cast(dict[str, Any], x)) for x in self.parameters
            ]


@dataclass(slots=True)
class CountriesResponse(_ResponseBase[Country]):
    """Representation of the API response for countries resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of country records.
    """

    results: list[Country]


# Instruments


@dataclass(slots=True)
class Instrument(_ResourceBase):
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

    def __post_init__(self) -> None:
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.manufacturer, dict):
            self.manufacturer = ManufacturerBase.load(self.manufacturer)


@dataclass(slots=True)
class InstrumentsResponse(_ResponseBase[Instrument]):
    """Representation of the API response for instruments resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of instrument records.
    """

    results: list[Instrument]


# Licenses


@dataclass(slots=True)
class License(_ResourceBase):
    """Representation of license resource in OpenAQ.

    Attributes:
        id: unique identifier for license
        name: name of license
        commercial_use_allowed: boolean indicating if commercial use is allowed
        attribution_required: boolean indicating if attribution is required
        share_alike_required:boolean indicating if share alike is required
        modification_allowed: boolean indicating if modification is allowed
        redistribution_allowed:boolean indicating if redistribution is allowed
        source_url: URL of original source of license
    """

    id: int
    name: str
    commercial_use_allowed: bool
    attribution_required: bool
    share_alike_required: bool
    modification_allowed: bool
    redistribution_allowed: bool
    source_url: str | None = None


@dataclass(slots=True)
class LicensesResponse(_ResponseBase[License]):
    """Representation of the API response for licenses resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of license records.
    """

    results: list[License]


# Manufacturers


@dataclass(slots=True)
class Manufacturer(_ResourceBase):
    """Representation of manufacturer resource in OpenAQ.

    Attributes:
        id: unique identifier for manufacturer
        name: manufacturer name
        instruments: a list of instruments made by the manufacturer
    """

    id: int
    name: str
    instruments: list[InstrumentBase]

    def __post_init__(self) -> None:
        """Sets class attributes to correct type after checking input type."""
        self.instruments = [
            InstrumentBase.load(cast(dict[str, Any], x)) for x in self.instruments
        ]


@dataclass(slots=True)
class ManufacturersResponse(_ResponseBase[Manufacturer]):
    """Representation of the API response for manufacturers resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of manufacturer records.
    """

    results: list[Manufacturer]


# Measurements


@dataclass(slots=True)
class Summary(_ResourceBase):
    """Statistical summary of measurement values.

    Attributes:
        min: mininum value
        q02: 2nd percentile
        q25: 25th percentile
        median: median value/50th percentile
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
    sd: float | None
    avg: float | None = None


@dataclass(slots=True)
class Coverage(_ResourceBase):
    """Data coverage details for measurements.

    Attributes:
        expected_count: expected number of measurements in the period
        expected_interval:
        observed_count: observed number of measurements in the period
        observed_interval:
        percent_complete:
        percent_coverage: percentage value representing the coverage based on the observed count divded by the expected count of measurements.
        datetime_from: ISO 8601 timestamp
        datetime_to: ISO 8601 timestamp
    """

    expected_count: int
    expected_interval: str
    observed_count: int
    observed_interval: str
    percent_complete: float
    percent_coverage: float
    datetime_from: Datetime
    datetime_to: Datetime

    def __post_init__(self) -> None:
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.datetime_from, dict):
            self.datetime_from = Datetime.load(self.datetime_from)
        if isinstance(self.datetime_to, dict):
            self.datetime_to = Datetime.load(self.datetime_to)


@dataclass(slots=True)
class Period(_ResourceBase):
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

    def __post_init__(self) -> None:
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.datetime_from, dict):
            self.datetime_from = Datetime.load(self.datetime_from)
        if isinstance(self.datetime_to, dict):
            self.datetime_to = Datetime.load(self.datetime_to)


@dataclass(slots=True)
class Measurement(_ResourceBase):
    """Representation of measurement resource in OpenAQ.

    Attributes:
        period: object detailing the measurement period.
        value: measured value or mean value if aggregate to period.
        parameter: object representing the parameter measured by the sensor.
        coordinates: WGS84 coordinate values if location is mobile.
        coverage: object detailing the data coverage of the sensor for the period.
        summary: object with summary statistics of mueasurment values of the sensor for the period.
    """

    period: Period
    value: float
    parameter: ParameterBase
    coordinates: Coordinates | None
    summary: Summary
    coverage: Coverage

    def __post_init__(self) -> None:
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


@dataclass(slots=True)
class MeasurementsResponse(_ResponseBase[Measurement]):
    """Representation of the API response for measurements resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of measurement records.
    """

    results: list[Measurement]


# Owners


@dataclass(slots=True)
class Owner(_ResourceBase):
    """Detailed information about an owner in OpenAQ.

    Attributes:
        id: unique identifier for owner
        name: owner name
    """

    id: int
    name: str


@dataclass(slots=True)
class OwnersResponse(_ResponseBase[Owner]):
    """Representation of the API response for owners resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of owner records.
    """

    results: list[Owner]


# Sensors


@dataclass(slots=True)
class LatestBase(_ResourceBase):
    """latest measurement.

    Attributes:
        datetime: datetime object
        value: measured value
        coordinates: coordinates object with latitude and longitude of measurement
    """

    datetime: Datetime
    value: float
    coordinates: Coordinates

    def __post_init__(self) -> None:
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.datetime, dict):
            self.datetime = Datetime.load(self.datetime)
        if isinstance(self.coordinates, dict):
            self.coordinates = Coordinates.load(self.coordinates)


@dataclass(slots=True)
class Sensor(_ResourceBase):
    """Detailed information about a sensor in OpenAQ.

    Attributes:
        id: unique identifier for sensor
        name: sensor name
        parameter: object representing the parameter measured by the sensor.
        datetime_first: datetime value representing first value available for the sensor.
        datetime_last: datetime value representing last value available for the sensor.
        coverage: object detailing the data coverage of the sensor
        latest: latest measurement value for the sensor
        summary: object with summary statistics of mueasurment values for the sensor
    """

    id: int
    name: str
    parameter: Parameter
    datetime_first: Datetime | None = None
    datetime_last: Datetime | None = None
    coverage: Coverage | None = None
    latest: LatestBase | None = None
    summary: Summary | None = None

    def __post_init__(self) -> None:
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.parameter, dict):
            self.parameter = Parameter.load(self.parameter)
        if isinstance(self.datetime_first, dict):
            self.datetime_first = Datetime.load(self.datetime_first)
        if isinstance(self.datetime_last, dict):
            self.datetime_last = Datetime.load(self.datetime_last)
        if isinstance(self.coverage, dict):
            self.coverage = Coverage.load(self.coverage)
        if isinstance(self.latest, dict):
            self.latest = LatestBase.load(self.latest)
        if isinstance(self.summary, dict):
            self.summary = Summary.load(self.summary)


@dataclass(slots=True)
class SensorsResponse(_ResponseBase[Sensor]):
    """Representation of the API response for sensors resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of sensor records.
    """

    results: list[Sensor]


@dataclass(slots=True)
class Latest(_ResourceBase):
    """Latest measurement.

    Attributes:
        datetime: datetime object
        value: measured value
        coordinates: coordinates object with latitude and longitude of measurement
        sensors_id: unique identifier for sensor
        locations_id: unique identifier for location
    """

    datetime: Datetime
    value: float
    coordinates: Coordinates
    sensors_id: int
    locations_id: int

    def __post_init__(self) -> None:
        """Sets class attributes to correct type after checking input type."""
        if isinstance(self.datetime, dict):
            self.datetime = Datetime.load(self.datetime)
        if isinstance(self.coordinates, dict):
            self.coordinates = Coordinates.load(self.coordinates)


@dataclass(slots=True)
class LatestResponse(_ResponseBase[Latest]):
    """Representation of the API response for latest resource.

    Attributes:
        meta: a metadata object containing information about the results.
        results: a list of latest records.
    """

    results: list[Latest]
