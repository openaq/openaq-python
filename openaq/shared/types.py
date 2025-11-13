"""Shared custom types."""

from typing import Literal, TypeAlias, TypedDict

_ROLLUP_VALUES = (
    'hourly',
    'daily',
    'monthly',
    'yearly',
    'hourofday',
    'dayofweek',
    'monthofyear',
)
Rollup: TypeAlias = Literal[
    'hourly', 'daily', 'monthly', 'yearly', 'hourofday', 'dayofweek', 'monthofyear'
]

_DATA_VALUES = ('measurements', 'hours', 'days', 'years')
Data: TypeAlias = Literal['measurements', 'hours', 'days', 'years']

_PARAMETER_TYPE_VALUES = ('pollutant', 'meteorological')
ParameterType: TypeAlias = Literal['pollutant', 'meteorological']

_SORT_ORDER_VALUES = ('ASC', 'DESC', 'asc', 'desc')
SortOrder: TypeAlias = Literal['ASC', 'DESC', 'asc', 'desc']

CoordinatesRadius: TypeAlias = tuple[tuple[float, float], int, None]

BboxOnly: TypeAlias = tuple[None, None, tuple[float, float, float, float]]


class OpenAQConfig(TypedDict):
    """Type definition for .openaq.toml configuration file."""

    api_key: str
