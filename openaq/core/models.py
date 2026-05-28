"""Shared utility functions for working with query parameter models."""

import datetime
from typing import Sequence

from .types import Data, Rollup


def build_query_params(
    **kwargs: (
        str
        | int
        | float
        | bool
        | Sequence[str | int | float | bool]
        | datetime.datetime
        | datetime.date
        | None
    ),
) -> dict[str, str | int | float | bool]:
    """Prepares keyword arguments to a dict for httpx query parameters.

    Loops through keyword args, if the value is of type list, tuple, or datetime.datetime,
    it makes appropriate conversions. This prevents httpx from splitting list or tuple types
    to individual query params e.g. coordinates=42,42 instead of coordinates=42&coordinates=42.
    For datetime.datetime types, it converts them to ISO 8601 formatted strings.

    Args:
        **kwargs: Arbitrary keyword arguments.

    Returns:
        dictionary of the prepared values.

    """
    params: dict[str, str | int | float | bool] = {}
    for k, v in kwargs.items():
        if v is None:
            continue
        if isinstance(v, (list, tuple)):
            params[k] = ",".join(str(x) for x in v)
        elif isinstance(
            v, datetime.date
        ):  # checks for both datetime and date since datetime is subclass of date
            params[k] = v.isoformat()
        elif isinstance(v, (str, int, float, bool)):
            params[k] = v
    return params


def build_measurements_path(
    sensors_id: int, data: Data, rollup: Rollup | None = None
) -> str:
    """Builds the path for measurements endpoint using data and rollup parameters.

    Args:
        sensors_id: sensors ID
        data: the base measurement unit to query. Options are 'measurements', 'hours', 'days', 'years'
        rollup: the period by which to rollup the base measurement data.

    Returns:
        string of url path
    """
    path = f'/sensors/{sensors_id}/{data}'

    if rollup:
        path += f'/{rollup}'

    return path
