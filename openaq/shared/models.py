"""Shared utility functions for working with query parameter models."""

from __future__ import annotations

import datetime
from typing import Any, Mapping

from .exceptions import NotFoundError
from .types import Data, Rollup


def build_query_params(**kwargs) -> Mapping[str, Any]:
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
    params = {}
    for k, v in kwargs.items():
        if v is not None:
            if isinstance(v, list) or isinstance(v, tuple):
                v = ",".join([str(x) for x in v])
            elif isinstance(v, datetime.datetime):
                v = v.isoformat()
            params[k] = v
    return params


def build_measurements_path(
    sensors_id: int, data: Data | None = None, rollup: Rollup | None = None
):
    """Prepares and builds the path for measurements endpoint using data and rollup parameters.

    Args:
        sensors_id: sensors ID
        data: the base measurement unit to query. options are 'measurements', 'hours', 'days', 'years'
        rollup: the period by which to rollup the base measurement data. Options are 'hourly', 'daily', 'yearly'

    Returns:
        string of url path

    Raises:
        NotFoundError:
    """
    base_path = f'/sensors/{sensors_id}'
    if data == 'measurements' and rollup in (
        'hourofday',
        'dayofweek',
        'monthofyear',
        'yearly',
    ):
        raise NotFoundError()
    if data == 'hours' and rollup == 'hourly':
        raise NotFoundError()
    if data == 'days' and rollup == 'daily':
        raise NotFoundError()
    if data == 'days' and rollup == 'hourofday':
        raise NotFoundError()
    if data == 'years' and rollup in ('monthly', 'yearly'):
        raise NotFoundError()
    if data == 'years' and rollup in ('hourofday', 'dayofweek', 'monthofyear'):
        raise NotFoundError()
    if data == 'measurements' or data == None:
        path = base_path + '/measurements'
    if data == 'hours':
        path = base_path + '/hours'
    if data == 'days':
        path = base_path + '/days'
    if data == 'years':
        path = base_path + '/years'
    if rollup:
        path += f'/{rollup}'
    return path
