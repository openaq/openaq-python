import pytest

from openaq.shared.models import build_query_params


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
