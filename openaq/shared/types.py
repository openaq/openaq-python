"""Shared customs types."""

from typing import Literal


Rollup = Literal['hourly', 'daily', 'yearly']
Data = Literal['measurements', 'hours', 'days', 'years']
