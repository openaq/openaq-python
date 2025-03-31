"""Shared custom types."""

from typing import Literal

Rollup = Literal[
    'hourly', 'daily', 'monthly', 'yearly', 'hourofday', 'dayofweek', 'monthofyear'
]
Data = Literal['measurements', 'hours', 'days', 'years']
