"""Shared custom types."""

from typing import Literal, TypeAlias, TypedDict, get_args

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

Data: TypeAlias = Literal['measurements', 'hours', 'days', 'years']
_DATA_VALUES = get_args(Data)

ParameterType: TypeAlias = Literal['pollutant', 'meteorological']
_PARAMETER_TYPE_VALUES = get_args(ParameterType)

SortOrder: TypeAlias = Literal['ASC', 'DESC', 'asc', 'desc']
_SORT_ORDER_VALUES = get_args(SortOrder)


CoordinatesRadius: TypeAlias = tuple[tuple[float, float], int, None]

BboxOnly: TypeAlias = tuple[None, None, tuple[float, float, float, float]]


class OpenAQConfig(TypedDict, total=False):
    """Type definition for .openaq.toml configuration file."""

    api_key: str | None
