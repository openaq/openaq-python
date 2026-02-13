from datetime import datetime

import pytest

from openaq.shared.models import build_measurements_path, build_query_params


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        ({}, {}),
        (
            {
                'page': 1,
                'limit': 100,
                "radius": 42,
                "coordinates": [32.3, 42.3],
                'bbox': [42.0, 42.0, 42.0, 42.0],
                "providers_id": 42,
                "countries_id": 42,
                "parameters_id": 2,
                'iso': 'us',
                'monitor': True,
                'mobile': False,
                'order_by': 'id',
                'sort_order': 'asc',
                'datetime_from': datetime(2024, 8, 22),
            },
            {
                'page': 1,
                'limit': 100,
                "radius": 42,
                "coordinates": '32.3,42.3',
                'bbox': '42.0,42.0,42.0,42.0',
                "providers_id": 42,
                "countries_id": 42,
                "parameters_id": 2,
                'iso': 'us',
                'monitor': True,
                'mobile': False,
                'order_by': 'id',
                'sort_order': 'asc',
                'datetime_from': '2024-08-22T00:00:00',
            },
        ),
        (
            {
                "providers_id": [1, 2, 3],
                "countries_id": [1, 2, 3],
                "parameters_id": [1, 2, 10],
            },
            {
                "providers_id": '1,2,3',
                "countries_id": '1,2,3',
                "parameters_id": '1,2,10',
            },
        ),
    ],
)
def test_build_query_params(kwargs, expected):
    params = build_query_params(**kwargs)
    assert expected == params


@pytest.mark.parametrize(
    "sensors_id, data, rollup, expected",
    [
        (42, 'measurements', None, "/sensors/42/measurements"),
        (42, 'measurements', 'hourly', "/sensors/42/measurements/hourly"),
        (42, 'hours', None, "/sensors/42/hours"),
        (42, 'days', 'monthly', "/sensors/42/days/monthly"),
        (99, 'years', None, "/sensors/99/years"),
    ],
)
def test_build_measurements_path(sensors_id, data, rollup, expected):
    path = build_measurements_path(sensors_id, data, rollup)
    assert path == expected
