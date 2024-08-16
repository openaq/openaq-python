import pytest

from openaq.shared.exceptions import NotFoundError
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
        (42, None, None, "/sensors/42/measurements"),
        (42, 'measurements', None, "/sensors/42/measurements"),
        (42, 'measurements', 'hourly', "/sensors/42/measurements/hourly"),
        (42, 'hours', None, "/sensors/42/hours"),
        (42, 'hours', 'daily', "/sensors/42/hours/daily"),
        (42, 'days', None, "/sensors/42/days"),
        (42, 'days', 'yearly', "/sensors/42/days/yearly"),
        (42, 'years', None, "/sensors/42/years"),
    ],
)
def test_build_measurements_path(sensors_id, data, rollup, expected):
    path = build_measurements_path(sensors_id, data, rollup)
    assert path == expected


@pytest.mark.parametrize(
    "sensors_id, data, rollup",
    [
        (
            42,
            'hours',
            'hourly',
        ),
        (
            42,
            'days',
            'daily',
        ),
        (
            42,
            'years',
            'yearly',
        ),
    ],
)
def test_build_measurements_path_throws(sensors_id, data, rollup):
    with pytest.raises(NotFoundError):
        build_measurements_path(sensors_id, data, rollup)
