"""Shared utility functions for working with query parameter models."""

import datetime
from collections.abc import Sequence

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

    Converts values into forms that encode correctly in a URL query string:

    - ``None`` values are dropped.
    - Lists and tuples are joined into a single comma-separated string,
      e.g. ``coordinates=42,42``. Without this, ``urllib.parse.urlencode``
      would encode the Python repr of the sequence (``[42, 42]``).
    - ``datetime.datetime`` and ``datetime.date`` values are converted to
      ISO 8601 strings.
    - ``str``, ``int``, ``float``, and ``bool`` values pass through
      unchanged. Booleans are lowercased later during encoding.
    
    Args:
        **kwargs: Arbitrary keyword arguments.

    Returns:
        dictionary of the prepared values.

    """
    params: dict[str, str | int | float | bool] = {}
    for k, v in kwargs.items():
        if v is None:
            continue
        if isinstance(v, list | tuple):
            params[k] = ",".join(str(x) for x in v)
        elif isinstance(
            v, datetime.date
        ):  # checks for both datetime and date since datetime is subclass of date
            params[k] = v.isoformat()
        elif isinstance(v, str | int | float | bool):
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
    path = f"/sensors/{sensors_id}/{data}"

    if rollup:
        path += f"/{rollup}"

    return path
