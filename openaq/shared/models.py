"""Shared utility functions for working with query parameter models."""

from __future__ import annotations

import datetime
from typing import Any, List, Mapping, Tuple, Union


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
