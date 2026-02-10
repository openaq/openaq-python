"""Shared custom types."""

from typing import Literal, TypeAlias, TypedDict

Rollup: TypeAlias = Literal[
    'hourly', 'daily', 'monthly', 'yearly', 'hourofday', 'dayofweek', 'monthofyear'
]

Data: TypeAlias = Literal['measurements', 'hours', 'days', 'years']

ParameterType: TypeAlias = Literal['pollutant', 'meteorological']

SortOrder: TypeAlias = Literal['ASC', 'DESC', 'asc', 'desc']

CoordinatesRadius: TypeAlias = tuple[tuple[float, float], int, None]

BboxOnly: TypeAlias = tuple[None, None, tuple[float, float, float, float]]


class OpenAQConfig(TypedDict, total=False):
    """Type definition for .openaq.toml configuration file."""

    api_key: str | None
