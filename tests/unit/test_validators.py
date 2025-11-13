import datetime
from openaq.shared.exceptions import IdentifierOutOfBoundsError, InvalidParameterError
import pytest
from hypothesis import given, strategies as st


from openaq.shared.validators import (
    data_check,
    datetime_check,
    geospatial_params_exclusivity_check,
    integer_id_check,
    is_int_list,
    iso8601_check,
    iso_check,
    limit_check,
    page_check,
    parameter_type_check,
    radius_check,
    rollup_check,
    to_datetime,
    validate_bbox,
    validate_coordinates,
    validate_data,
    validate_datetime_params,
    validate_geospatial_params,
    validate_integer_id,
    validate_iso_param,
    validate_limit_param,
    validate_mobile,
    validate_monitor,
    validate_order_by,
    validate_page_param,
    validate_radius,
    validate_rollup,
    validate_sort_order,
)


@pytest.mark.parametrize(
    "id,valid",
    [
        pytest.param(-1, False, id="negative-value"),
        pytest.param(0, False, id="zero-value"),
        pytest.param(1, True, id="minimum-valid"),
        pytest.param(2_147_483_647 - 1, True, id="one-below-max"),
        pytest.param(2_147_483_647, True, id="maximum-valid"),
        pytest.param(2_147_483_647 + 1, False, id="one-above-max"),
        pytest.param(999_999_999_999, False, id="far-above-max"),
        pytest.param(False, False, id="bool-false"),
        pytest.param(True, False, id="bool-true"),
        pytest.param({}, False, id="bool-true"),
        pytest.param([], False, id="bool-true"),
        pytest.param((), False, id="bool-true"),
    ],
)
def test_integer_id_check(id: int, valid: bool):
    assert integer_id_check(id) == valid


@pytest.mark.parametrize(
    "id",
    [
        pytest.param(-1, id="negative-value"),
        pytest.param(0, id="zero-value"),
        pytest.param(2_147_483_647 + 1, id="one-above-max"),
        pytest.param(999_999_999_999, id="far-above-max"),
    ],
)
def test_validate_integer_id_throws(id: int):
    with pytest.raises(IdentifierOutOfBoundsError):
        validate_integer_id(id)


@pytest.mark.parametrize(
    "id",
    [
        pytest.param(1, id="minimum-valid"),
        pytest.param(42, id="typical-value"),
        pytest.param(9999, id="medium-value"),
        pytest.param(2_147_483_647, id="maximum-valid"),
    ],
)
def test_validate_integer_id_passes(id: int):
    assert validate_integer_id(id) == id


@pytest.mark.parametrize(
    "radius,valid",
    [
        pytest.param(0, False, id="zero-radius"),
        pytest.param(1, True, id="minimum-valid"),
        pytest.param(25_000, True, id="maximum-valid"),
        pytest.param(25_001, False, id="one-above-max"),
        pytest.param("1", False, id="string-one"),
        pytest.param("-1", False, id="string-negative"),
        pytest.param(-1, False, id="negative-integer"),
        pytest.param(True, False, id="bool-true"),
        pytest.param(False, False, id="bool-false"),
    ],
)
def test_radius_check(radius: int, valid: bool):
    assert radius_check(radius) == valid


@pytest.mark.parametrize(
    "radius",
    [
        pytest.param(1, id="minimum-valid"),
        pytest.param(42, id="typical-value"),
        pytest.param(25_000, id="maximum-valid"),
    ],
)
def test_validate_radius(radius: int):
    assert validate_radius(radius) == radius


@pytest.mark.parametrize(
    "radius",
    [
        pytest.param(0, id="zero-radius"),
        pytest.param(25_001, id="one-above-max"),
        pytest.param("1", id="string-one"),
        pytest.param("-1", id="string-negative"),
        pytest.param(-1, id="negative-integer"),
    ],
)
def test_validate_radius_throws(radius):
    with pytest.raises(InvalidParameterError):
        validate_radius(radius)


@pytest.mark.parametrize(
    "coordinates",
    [
        pytest.param((-18.9185, 47.5211), id="typical-coordinates"),
        pytest.param((0.0, 0.0), id="zero-zero"),
        pytest.param((90.0, 180.0), id="maximum-valid"),
        pytest.param((-90.0, -180.0), id="minimum-valid"),
        pytest.param((62, -114), id="integer-coordinates"),
        pytest.param((0, 0), id="integer-zero-zero"),
        pytest.param((90, 0), id="north-pole"),
        pytest.param((0, 180), id="equator-antimeridian"),
    ],
)
def test_validate_coordinates(coordinates):
    assert validate_coordinates(coordinates) == coordinates


@pytest.mark.parametrize(
    "coordinates",
    [
        pytest.param(None, id="none-value"),
        pytest.param("-18.9185,47.5211", id="string-instead-of-tuple"),
        pytest.param([-18.9185, 47.5211], id="list-instead-of-tuple"),
        pytest.param({"lat": -18.9185, "lon": 47.5211}, id="dict-instead-of-tuple"),
        pytest.param(42, id="single-number"),
        pytest.param((), id="empty-tuple"),
        pytest.param((-18.9185,), id="one-element-tuple"),
        pytest.param((-18.9185, 47.5211, 0), id="three-element-tuple"),
        pytest.param((-18.9185, 47.5211, 0, 0), id="four-element-tuple"),
        pytest.param(("-18.9185", "47.5211"), id="all-string-elements"),
        pytest.param((-18.9185, "47.5211"), id="mixed-string-element"),
        pytest.param((None, 47.5211), id="none-in-first-position"),
        pytest.param((-18.9185, None), id="none-in-second-position"),
        pytest.param((91.0, 0.0), id="latitude-above-max"),
        pytest.param((-91.0, 0.0), id="latitude-below-min"),
        pytest.param((0.0, 181.0), id="longitude-above-max"),
        pytest.param((0.0, -181.0), id="longitude-below-min"),
        pytest.param((91.0, 181.0), id="both-coordinates-above-max"),
        pytest.param((-91.0, -181.0), id="both-coordinates-below-min"),
    ],
)
def test_validate_coordinates_throws(coordinates):
    with pytest.raises(InvalidParameterError):
        validate_coordinates(coordinates)


@pytest.mark.parametrize(
    "bbox",
    [
        pytest.param(
            (30.990200, -17.876409, 31.113796, -17.818320),
            id="valid-harare-zimbabwe-area-bbox",
        ),
        pytest.param((-180.0, -90.0, 180.0, 90.0), id="valid-entire-world-bbox"),
        pytest.param((-10, -10, 10, 10), id="valid-bbox-with-integers"),
        pytest.param((106.81, 47.87, 107.05, 47.95), id="valid-mongolia-area"),
        pytest.param((0, 0, 0.001, 0.001), id="valid-very-small-box"),
        pytest.param((-180, -90, 0, 0), id="valid-southwest-min"),
        pytest.param((0, 0, 180, 90), id="valid-northeast-max"),
        pytest.param(
            (-180.0, -90.0, -179.0, -89.0), id="valid-bbox-near-minimum-corner"
        ),
        pytest.param((179.0, 89.0, 180.0, 90.0), id="valid-bbox-near-maximum-corner"),
        pytest.param((-180.0, -90.0, 0.0, 0.0), id="valid-bbox-from-min-to-center"),
        pytest.param((0.0, 0.0, 180.0, 90.0), id="valid-bbox-from-center-to-max"),
        pytest.param((-180.0, 40.1, -179.0, 40.2), id="valid-bbox-on-min-lon-boundary"),
        pytest.param((179.0, 40.1, 180.0, 40.2), id="valid-bbox-on-max-lon-boundary"),
        pytest.param((44.2, -90.0, 44.8, -89.0), id="valid-bbox-on-min-lat-boundary"),
        pytest.param((44.2, 89.0, 44.8, 90.0), id="valid-bbox-on-max-lat-boundary"),
        pytest.param((0.0, 0.0, 0.0001, 0.0001), id="valid-tiny-bbox"),
        pytest.param((-122.419, 37.774, -122.418, 37.775), id="valid-one-block-bbox"),
        pytest.param((-74, 40.1, -73, 40.2), id="valid-mixed-int-and-float-type-1"),
        pytest.param((44.2, 40, 44.8, 41), id="valid-mixed-int-and-float-type-2"),
        pytest.param((-74, 40, 44.8, 40.2), id="valid-mixed-int-and-float-type-3"),
    ],
)
def test_validate_bbox(bbox):
    validate_bbox(bbox) == bbox


@pytest.mark.parametrize(
    "bbox",
    [
        pytest.param(None, id="none-value"),
        pytest.param("44.2,40.1,44.8,40.2", id="string-instead-of-tuple"),
        pytest.param([44.2, 40.1, 44.8, 40.2], id="list-instead-of-tuple"),
        pytest.param(
            {"min_lon": 44.2, "min_lat": 40.1}, id="dictionary-instead-of-tuple"
        ),
        pytest.param(42, id="single-number-instead-of-tuple"),
        pytest.param((), id="empty-tuple"),
        pytest.param((44.2,), id="tuple-with-one-element"),
        pytest.param((44.2, 40.1), id="tuple-with-two-elements"),
        pytest.param((44.2, 40.1, 44.8), id="tuple-with-three-elements"),
        pytest.param((44.2, 40.1, 44.8, 40.2, 0), id="tuple-with-five-elements"),
        pytest.param((44.2, 40.1, 44.8, 40.2, 0, 0), id="tuple-with-six-elements"),
        pytest.param(("44.2", "40.1", "44.8", "40.2"), id="all-string-elements"),
        pytest.param((44.2, 40.1, "44.8", 40.2), id="one-string-element"),
        pytest.param((None, 40.1, 44.8, 40.2), id="none-in-first-position"),
        pytest.param((44.2, None, 44.8, 40.2), id="none-in-second-position"),
        pytest.param((44.2, 40.1, None, 40.2), id="none-in-third-position"),
        pytest.param((44.2, 40.1, 44.8, None), id="none-in-fourth-position"),
        pytest.param((44.2, 91.0, 44.8, 92.0), id="both-latitudes-too-high"),
        pytest.param((44.2, -91.0, 44.8, -90.5), id="min-lat-too-low"),
        pytest.param((44.2, 40.1, 44.8, 91.0), id="max-lat-too-high"),
        pytest.param((44.2, -91.0, 44.8, 40.2), id="min-lat-below-valid-range"),
        pytest.param((44.2, 100.0, 44.8, 101.0), id="latitudes-way-out-of-range"),
        pytest.param((-181.0, 40.1, -180.5, 40.2), id="min-lon-too-low"),
        pytest.param((179.0, 40.1, 181.0, 40.2), id="max-lon-too-high"),
        pytest.param((-181.0, 40.1, 44.8, 40.2), id="min-lon-below-valid-range"),
        pytest.param((44.2, 40.1, 181.0, 40.2), id="max-lon-above-valid-range"),
        pytest.param((200.0, 40.1, 201.0, 40.2), id="longitudes-way-out-of-range"),
        pytest.param((44.8, 40.1, 44.2, 40.2), id="min-lon-greater-than-max-lon"),
        pytest.param((44.2, 40.1, 44.2, 40.2), id="min-lon-equals-max-lon"),
        pytest.param((10.0, 40.1, 10.0, 40.2), id="min-lon-equals-max-lon-at-10"),
        pytest.param(
            (10.0, 40.1, 5.0, 40.2),
            id="min-lon-greater-than-max-lon-positive-values",
        ),
        pytest.param((44.2, 40.2, 44.8, 40.1), id="min-lat-greater-than-max-lat"),
        pytest.param((44.2, 40.1, 44.8, 40.1), id="min-lat-equals-max-lat"),
        pytest.param((44.2, 45.0, 44.8, 45.0), id="min-lat-equals-max-lat-at-45"),
        pytest.param(
            (44.2, 50.0, 44.8, 40.1),
            id="min-lat-greater-than-max-lat-positive-values",
        ),
        pytest.param((10.0, 50.0, 10.0, 40.1), id="both-min-equal-max-and-inverted"),
        pytest.param((10.0, 50.0, 5.0, 40.1), id="both-coordinates-inverted"),
        pytest.param((-180.0001, 40.1, -179.0, 40.2), id="min-lon-just-below-boundary"),
        pytest.param((179.0, 40.1, 180.0001, 40.2), id="max-lon-just-above-boundary"),
        pytest.param((44.2, -90.0001, 44.8, -89.0), id="min-lat-just-below-boundary"),
        pytest.param((44.2, 89.0, 44.8, 90.0001), id="max-lat-just-above-boundary"),
    ],
)
def test_validate_bbox_throws(bbox):
    with pytest.raises(InvalidParameterError):
        validate_bbox(bbox)


@pytest.mark.parametrize(
    "coordinates,radius,bbox,valid",
    [
        pytest.param(None, None, None, True, id="no-parameters"),
        pytest.param((0.0, 0.0), 1000, None, True, id="coordinates-and-radius"),
        pytest.param(None, None, (0, 0, 1, 1), True, id="bbox-only"),
        pytest.param((0.0, 0.0), None, None, False, id="coordinates-without-radius"),
        pytest.param(None, 1000, None, False, id="radius-without-coordinates"),
        pytest.param((0.0, 0.0), None, (0, 0, 1, 1), False, id="bbox-with-coordinates"),
        pytest.param(None, 1000, (0, 0, 1, 1), False, id="bbox-with-radius"),
    ],
)
def test_geospatial_params_exclusivity_check(coordinates, radius, bbox, valid):
    assert geospatial_params_exclusivity_check(coordinates, radius, bbox) == valid


@pytest.mark.parametrize(
    "coordinates,radius,bbox,expected",
    [
        pytest.param(None, None, None, (None, None, None), id="no-parameters"),
        pytest.param(
            (0.0, 0.0),
            1000,
            None,
            ((0.0, 0.0), 1000, None),
            id="coordinates-and-radius",
        ),
        pytest.param(
            (35.0844, 106.6504),
            5000,
            None,
            ((35.0844, 106.6504), 5000, None),
            id="coordinates-and-radius-typical",
        ),
        pytest.param(
            (-90.0, -180.0),
            25000,
            None,
            ((-90.0, -180.0), 25000, None),
            id="coordinates-and-radius-at-extremes",
        ),
        pytest.param(
            None,
            None,
            (0.0, 0.0, 1.0, 1.0),
            (None, None, (0.0, 0.0, 1.0, 1.0)),
            id="bbox-only",
        ),
        pytest.param(
            None,
            None,
            (-180.0, -90.0, 180.0, 90.0),
            (None, None, (-180.0, -90.0, 180.0, 90.0)),
            id="bbox-only-world",
        ),
        pytest.param(
            None,
            None,
            (44.2, 40.1, 44.8, 40.2),
            (None, None, (44.2, 40.1, 44.8, 40.2)),
            id="bbox-only-typical",
        ),
    ],
)
def test_validate_geospatial_params(coordinates, radius, bbox, expected):
    assert validate_geospatial_params(coordinates, radius, bbox) == expected


@pytest.mark.parametrize(
    "coordinates,radius,bbox",
    [
        pytest.param(None, None, None, id="no-parameters"),
        pytest.param((0.0, 0.0), 1000, None, id="coordinates-and-radius"),
        pytest.param(
            (35.0844, 106.6504), 5000, None, id="coordinates-and-radius-typical"
        ),
        pytest.param(
            (-90.0, -180.0), 25000, None, id="coordinates-and-radius-extremes"
        ),
        pytest.param(
            (90.0, 180.0), 1, None, id="coordinates-and-radius-max-coords-min-radius"
        ),
        pytest.param(None, None, (0.0, 0.0, 1.0, 1.0), id="bbox-only"),
        pytest.param(None, None, (-180.0, -90.0, 180.0, 90.0), id="bbox-only-world"),
        pytest.param(None, None, (44.2, 40.1, 44.8, 40.2), id="bbox-only-typical"),
    ],
)
def test_validate_geospatial_params_passes(coordinates, radius, bbox):
    result = validate_geospatial_params(coordinates, radius, bbox)
    assert result == (coordinates, radius, bbox)


@pytest.mark.parametrize(
    "coordinates,radius,bbox,expected_error",
    [
        pytest.param(
            (0.0, 0.0),
            None,
            None,
            "coordinates requires radius parameter",
            id="coordinates-without-radius",
        ),
        pytest.param(
            (35.0844, 106.6504),
            None,
            None,
            "coordinates requires radius parameter",
            id="coordinates-without-radius-typical",
        ),
        pytest.param(
            None,
            1000,
            None,
            "radius requires coordinates parameter",
            id="radius-without-coordinates",
        ),
        pytest.param(
            None,
            5000,
            None,
            "radius requires coordinates parameter",
            id="radius-without-coordinates-typical",
        ),
        pytest.param(
            (0.0, 0.0),
            None,
            (0.0, 0.0, 1.0, 1.0),
            "coordinates requires radius parameter",
            id="bbox-with-coordinates",
        ),
        pytest.param(
            None,
            1000,
            (0.0, 0.0, 1.0, 1.0),
            "radius requires coordinates parameter",
            id="bbox-with-radius",
        ),
        pytest.param(
            (0.0, 0.0),
            1000,
            (0.0, 0.0, 1.0, 1.0),
            "bbox cannot be used with coordinates/radius parameters",
            id="bbox-with-coordinates-and-radius",
        ),
    ],
)
def test_validate_geospatial_params_throws_exclusivity_errors(
    coordinates, radius, bbox, expected_error
):
    with pytest.raises(InvalidParameterError) as exc_info:
        validate_geospatial_params(coordinates, radius, bbox)
    assert str(exc_info.value) == expected_error


@pytest.mark.parametrize(
    "coordinates,radius,bbox",
    [
        pytest.param("invalid", 1000, None, id="invalid-coordinates-string"),
        pytest.param([0.0, 0.0], 1000, None, id="invalid-coordinates-list"),
        pytest.param(
            (91.0, 0.0), 1000, None, id="invalid-coordinates-lat-out-of-range"
        ),
        pytest.param(
            (0.0, 181.0), 1000, None, id="invalid-coordinates-lon-out-of-range"
        ),
        pytest.param(
            (0.0, 0.0, 0.0), 1000, None, id="invalid-coordinates-wrong-length"
        ),
        pytest.param((0.0, 0.0), 0, None, id="invalid-radius-zero"),
        pytest.param((0.0, 0.0), 25001, None, id="invalid-radius-above-max"),
        pytest.param((0.0, 0.0), -1, None, id="invalid-radius-negative"),
        pytest.param((0.0, 0.0), "1000", None, id="invalid-radius-string"),
        pytest.param(None, None, "invalid", id="invalid-bbox-string"),
        pytest.param(None, None, [0.0, 0.0, 1.0, 1.0], id="invalid-bbox-list"),
        pytest.param(None, None, (0.0, 0.0, 1.0), id="invalid-bbox-wrong-length"),
        pytest.param(
            None, None, (1.0, 0.0, 0.0, 1.0), id="invalid-bbox-min-lon-greater-than-max"
        ),
        pytest.param(
            None, None, (0.0, 1.0, 1.0, 0.0), id="invalid-bbox-min-lat-greater-than-max"
        ),
        pytest.param(
            None, None, (-181.0, 0.0, 0.0, 1.0), id="invalid-bbox-lon-out-of-range"
        ),
        pytest.param(
            None, None, (0.0, -91.0, 1.0, 0.0), id="invalid-bbox-lat-out-of-range"
        ),
    ],
)
def test_validate_geospatial_params_throws_validation_errors(coordinates, radius, bbox):
    """Test that invalid parameter values are caught by sub-validators."""
    with pytest.raises(InvalidParameterError):
        validate_geospatial_params(coordinates, radius, bbox)


@pytest.mark.parametrize(
    "page,valid",
    [
        pytest.param(1, True, id="one"),
        pytest.param(2, True, id="two"),
        pytest.param(10, True, id="ten"),
        pytest.param(100, True, id="hundred"),
        pytest.param(9999, True, id="large-value"),
        pytest.param(0, False, id="zero"),
        pytest.param(-1, False, id="negative-one"),
        pytest.param(-100, False, id="negative-large"),
        pytest.param(1.0, False, id="float-one"),
        pytest.param(1.5, False, id="float-decimal"),
        pytest.param("1", False, id="string-one"),
        pytest.param("10", False, id="string-ten"),
        pytest.param("page", False, id="string-text"),
        pytest.param(None, False, id="none"),
        pytest.param(True, False, id="boolean-true"),
        pytest.param(False, False, id="boolean-false"),
        pytest.param([1], False, id="list-with-one"),
        pytest.param((1,), False, id="tuple-with-one"),
        pytest.param({"page": 1}, False, id="dict"),
        pytest.param([], False, id="empty-list"),
        pytest.param({}, False, id="empty-dict"),
        pytest.param("", False, id="empty-string"),
    ],
)
def test_page_check(page, valid):
    assert page_check(page) == valid


@pytest.mark.parametrize(
    "page",
    [
        pytest.param(1, id="one"),
        pytest.param(2, id="two"),
        pytest.param(10, id="ten"),
        pytest.param(100, id="hundred"),
        pytest.param(9999, id="large-value"),
        pytest.param(2_147_483_647, id="max-int"),
    ],
)
def test_validate_page_param(page):
    assert validate_page_param(page) == page


@pytest.mark.parametrize(
    "page",
    [
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative-one"),
        pytest.param(-100, id="negative-large"),
        pytest.param(1.0, id="float-one"),
        pytest.param(1.5, id="float-decimal"),
        pytest.param("1", id="string-one"),
        pytest.param("10", id="string-ten"),
        pytest.param("page", id="string-text"),
        pytest.param(None, id="none"),
        pytest.param(True, id="boolean-true"),
        pytest.param(False, id="boolean-false"),
        pytest.param([1], id="list-with-one"),
        pytest.param((1,), id="tuple-with-one"),
        pytest.param({"page": 1}, id="dict"),
        pytest.param([], id="empty-list"),
        pytest.param({}, id="empty-dict"),
        pytest.param("", id="empty-string"),
    ],
)
def test_validate_page_param_throws(page):
    with pytest.raises(InvalidParameterError):
        validate_page_param(page)


@pytest.mark.parametrize(
    "limit,valid",
    [
        pytest.param(1, True, id="one"),
        pytest.param(2, True, id="two"),
        pytest.param(10, True, id="ten"),
        pytest.param(100, True, id="hundred"),
        pytest.param(999, True, id="nine-ninety-nine"),
        pytest.param(1000, True, id="one-thousand-max-limit"),
        pytest.param(0, False, id="zero"),
        pytest.param(-1, False, id="negative-one"),
        pytest.param(-100, False, id="negative-large"),
        pytest.param(1001, False, id="one-thousand-one-above-max"),
        pytest.param(10000, False, id="ten-thousand"),
        pytest.param(1.0, False, id="float-one"),
        pytest.param(10.5, False, id="float-decimal"),
        pytest.param(999.9, False, id="float-near-max"),
        pytest.param("1", False, id="string-one"),
        pytest.param("100", False, id="string-hundred"),
        pytest.param("limit", False, id="string-text"),
        pytest.param(None, False, id="none"),
        pytest.param(True, False, id="boolean-true"),
        pytest.param(False, False, id="boolean-false"),
        pytest.param([], False, id="empty-list"),
        pytest.param({}, False, id="empty-dict"),
        pytest.param("", False, id="empty-string"),
    ],
)
def test_limit_check(limit, valid):
    assert limit_check(limit) == valid


@pytest.mark.parametrize(
    "limit",
    [
        pytest.param(1, id="one"),
        pytest.param(2, id="two"),
        pytest.param(100, id="hundred"),
        pytest.param(999, id="nine-ninety-nine"),
        pytest.param(1000, id="one-thousand-max-limit"),
    ],
)
def test_validate_limit_param(limit):
    assert validate_limit_param(limit) == limit


@pytest.mark.parametrize(
    "limit",
    [
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
        pytest.param(1001, id="above-max-limit"),
        pytest.param(1.0, id="float"),
        pytest.param("1", id="string"),
        pytest.param(None, id="none"),
        pytest.param(True, id="boolean-true"),
        pytest.param([1], id="list"),
    ],
)
def test_validate_limit_param_throws(limit):
    with pytest.raises(InvalidParameterError):
        validate_limit_param(limit)


@pytest.mark.parametrize(
    "id_list,valid",
    [
        pytest.param([1], True, id="single-valid"),
        pytest.param([1, 2, 3], True, id="multiple-valid"),
        pytest.param([1, 100, 9999, 2_147_483_647], True, id="various-valid-integers"),
        pytest.param([], True, id="empty-list"),
        pytest.param([0], False, id="contains-zero"),
        pytest.param([-1], False, id="contains-negative"),
        pytest.param([2_147_483_648], False, id="contains-above-int-32"),
        pytest.param([1, 2, 0], False, id="mixed-with-zero"),
        pytest.param([1, -1, 3], False, id="mixed-with-negative"),
        pytest.param([1, 2_147_483_648], False, id="mixed-with-above-int-32"),
        pytest.param([1.0], False, id="contains-float"),
        pytest.param(["1"], False, id="contains-string"),
        pytest.param([None], False, id="contains-none"),
        pytest.param([True], False, id="contains-boolean"),
        pytest.param([[1]], False, id="contains-list"),
        pytest.param([1, 2, "3"], False, id="mixed-with-string"),
        pytest.param([1, 2.0, 3], False, id="mixed-with-float"),
        pytest.param([1, None, 3], False, id="mixed-with-none"),
    ],
)
def test_is_int_list(id_list, valid):
    assert is_int_list(id_list) == valid


@pytest.mark.parametrize(
    "iso,valid",
    [
        pytest.param("US", True, id="valid-uppercase"),
        pytest.param("us", True, id="valid-lowercase"),
        pytest.param("Us", True, id="valid-mixed-case"),
        pytest.param("USA", False, id="invalid-uppercase"),
        pytest.param("usa", False, id="invalid-lowercase"),
        pytest.param("UsA", False, id="invalid-mixed-case"),
        pytest.param(False, False, id="invalid-bool-false"),
        pytest.param(True, False, id="invalid-bool-true"),
        pytest.param([], False, id="invalid-list"),
        pytest.param((), False, id="invalid-tuple"),
        pytest.param({}, False, id="invalid-dict"),
        pytest.param(None, False, id="invalid-none"),
    ],
)
def test_iso_check(iso, valid):
    assert iso_check(iso) == valid


@pytest.mark.parametrize(
    "code",
    [
        pytest.param("USA", id="three-letters-uppercase"),
        pytest.param("usa", id="three-letters-lowercase"),
        pytest.param("U", id="one-letter"),
        pytest.param("12", id="numeric"),
        pytest.param("", id="empty-string"),
        pytest.param("ZZ", id="invalid-code"),
        pytest.param(123, id="integer"),
        pytest.param(None, id="none"),
        pytest.param(True, id="bool-true"),
        pytest.param(False, id="bool-false"),
    ],
)
def test_validate_iso_param_throws(code: str):
    with pytest.raises(InvalidParameterError):
        validate_iso_param(code)


@pytest.mark.parametrize(
    "code",
    [
        pytest.param("US", id="valid-uppercase"),
        pytest.param("us", id="valid-lowercase"),
        pytest.param("Us", id="valid-mixed-case"),
        pytest.param("GB", id="valid-gb"),
        pytest.param("de", id="valid-de"),
    ],
)
def test_validate_iso_param_returns_code(code: str):
    assert validate_iso_param(code) == code


@pytest.mark.parametrize(
    "monitor,valid",
    [
        pytest.param(True, True, id="true"),
        pytest.param(False, True, id="false"),
        pytest.param(1, False, id="integer-one"),
        pytest.param(0, False, id="integer-zero"),
        pytest.param("true", False, id="string-true"),
        pytest.param("false", False, id="string-false"),
        pytest.param("True", False, id="string-True"),
        pytest.param("False", False, id="string-False"),
        pytest.param(None, False, id="none"),
        pytest.param([], False, id="empty-list"),
        pytest.param({}, False, id="empty-dict"),
        pytest.param((), False, id="empty-tuple"),
        pytest.param("", False, id="empty-string"),
    ],
)
def test_validate_monitor(monitor: object, valid: bool):
    if valid:
        assert validate_monitor(monitor) == monitor
    else:
        with pytest.raises(InvalidParameterError):
            validate_monitor(monitor)


@pytest.mark.parametrize(
    "mobile,valid",
    [
        pytest.param(True, True, id="true"),
        pytest.param(False, True, id="false"),
        pytest.param(1, False, id="integer-one"),
        pytest.param(0, False, id="integer-zero"),
        pytest.param("true", False, id="string-true"),
        pytest.param("false", False, id="string-false"),
        pytest.param("True", False, id="string-True"),
        pytest.param("False", False, id="string-False"),
        pytest.param(None, False, id="none"),
        pytest.param([], False, id="empty-list"),
        pytest.param({}, False, id="empty-dict"),
        pytest.param((), False, id="empty-tuple"),
        pytest.param("", False, id="empty-string"),
    ],
)
def test_validate_mobile(mobile: object, valid: bool):
    if valid:
        assert validate_mobile(mobile) == mobile
    else:
        with pytest.raises(InvalidParameterError):
            validate_mobile(mobile)


@pytest.mark.parametrize(
    "order_by,valid",
    [
        pytest.param("id", True, id="valid-id"),
        pytest.param("name", True, id="valid-name"),
        pytest.param("created", True, id="valid-created"),
        pytest.param("", True, id="empty-string"),
        pytest.param("any_string", True, id="any-string"),
        pytest.param(123, False, id="integer"),
        pytest.param(True, False, id="bool-true"),
        pytest.param(False, False, id="bool-false"),
        pytest.param(None, False, id="none"),
        pytest.param([], False, id="empty-list"),
        pytest.param({}, False, id="empty-dict"),
        pytest.param((), False, id="empty-tuple"),
    ],
)
def test_validate_order_by(order_by: object, valid: bool):
    if valid:
        assert validate_order_by(order_by) == order_by
    else:
        with pytest.raises(InvalidParameterError):
            validate_order_by(order_by)


@pytest.mark.parametrize(
    "sort_order,valid",
    [
        pytest.param("ASC", True, id="valid-asc-uppercase"),
        pytest.param("DESC", True, id="valid-desc-uppercase"),
        pytest.param("asc", True, id="valid-asc-lowercase"),
        pytest.param("desc", True, id="valid-desc-lowercase"),
        pytest.param("Asc", False, id="invalid-mixed-case-asc"),
        pytest.param("Desc", False, id="invalid-mixed-case-desc"),
        pytest.param("ascending", False, id="invalid-ascending"),
        pytest.param("descending", False, id="invalid-descending"),
        pytest.param("", False, id="empty-string"),
        pytest.param("invalid", False, id="invalid-string"),
        pytest.param(123, False, id="integer"),
        pytest.param(True, False, id="bool-true"),
        pytest.param(False, False, id="bool-false"),
        pytest.param(None, False, id="none"),
        pytest.param([], False, id="empty-list"),
        pytest.param({}, False, id="empty-dict"),
        pytest.param((), False, id="empty-tuple"),
    ],
)
def test_validate_sort_order(sort_order: object, valid: bool):
    if valid:
        assert validate_sort_order(sort_order) == sort_order
    else:
        with pytest.raises(InvalidParameterError):
            validate_sort_order(sort_order)


@pytest.mark.parametrize(
    "data,valid",
    [
        pytest.param("measurements", True, id="valid-measurements"),
        pytest.param("hours", True, id="valid-hours"),
        pytest.param("days", True, id="valid-days"),
        pytest.param("years", True, id="valid-years"),
        pytest.param("Measurements", False, id="invalid-uppercase"),
        pytest.param("HOURS", False, id="invalid-all-caps"),
        pytest.param("Days", False, id="invalid-mixed-case"),
        pytest.param("measurement", False, id="invalid-singular"),
        pytest.param("", False, id="empty-string"),
        pytest.param("invalid", False, id="invalid-string"),
        pytest.param(123, False, id="integer"),
        pytest.param(True, False, id="bool-true"),
        pytest.param(False, False, id="bool-false"),
        pytest.param(None, False, id="none"),
        pytest.param([], False, id="empty-list"),
        pytest.param({}, False, id="empty-dict"),
        pytest.param((), False, id="empty-tuple"),
    ],
)
def test_data_check(data: object, valid: bool):
    assert data_check(data) == valid


@pytest.mark.parametrize(
    "data",
    [
        pytest.param("Measurements", id="invalid-uppercase"),
        pytest.param("HOURS", id="invalid-all-caps"),
        pytest.param("measurement", id="invalid-singular"),
        pytest.param("", id="empty-string"),
        pytest.param("invalid", id="invalid-string"),
        pytest.param(123, id="integer"),
        pytest.param(None, id="none"),
    ],
)
def test_validate_data_throws(data: object):
    with pytest.raises(InvalidParameterError):
        validate_data(data)


@pytest.mark.parametrize(
    "data",
    [
        pytest.param("measurements", id="valid-measurements"),
        pytest.param("hours", id="valid-hours"),
        pytest.param("days", id="valid-days"),
        pytest.param("years", id="valid-years"),
    ],
)
def test_validate_data_returns_data(data: object):
    assert validate_data(data) == data


@pytest.mark.parametrize(
    "rollup,valid",
    [
        pytest.param("hourly", True, id="valid-hourly"),
        pytest.param("daily", True, id="valid-daily"),
        pytest.param("monthly", True, id="valid-monthly"),
        pytest.param("yearly", True, id="valid-yearly"),
        pytest.param("hourofday", True, id="valid-hourofday"),
        pytest.param("dayofweek", True, id="valid-dayofweek"),
        pytest.param("monthofyear", True, id="valid-monthofyear"),
        pytest.param("Hourly", False, id="invalid-uppercase"),
        pytest.param("DAILY", False, id="invalid-all-caps"),
        pytest.param("Monthly", False, id="invalid-mixed-case"),
        pytest.param("hour", False, id="invalid-partial"),
        pytest.param("", False, id="empty-string"),
        pytest.param("invalid", False, id="invalid-string"),
        pytest.param(123, False, id="integer"),
        pytest.param(True, False, id="bool-true"),
        pytest.param(False, False, id="bool-false"),
        pytest.param(None, False, id="none"),
        pytest.param([], False, id="empty-list"),
        pytest.param({}, False, id="empty-dict"),
        pytest.param((), False, id="empty-tuple"),
    ],
)
def test_rollup_check(rollup: object, valid: bool):
    assert rollup_check(rollup) == valid


@pytest.mark.parametrize(
    "rollup",
    [
        pytest.param("Hourly", id="invalid-uppercase"),
        pytest.param("DAILY", id="invalid-all-caps"),
        pytest.param("hour", id="invalid-partial"),
        pytest.param("", id="empty-string"),
        pytest.param("invalid", id="invalid-string"),
        pytest.param(123, id="integer"),
        pytest.param(None, id="none"),
    ],
)
def test_validate_rollup_throws(rollup: object):
    with pytest.raises(InvalidParameterError):
        validate_rollup(rollup)


@pytest.mark.parametrize(
    "rollup",
    [
        pytest.param("hourly", id="valid-hourly"),
        pytest.param("daily", id="valid-daily"),
        pytest.param("monthly", id="valid-monthly"),
        pytest.param("yearly", id="valid-yearly"),
        pytest.param("hourofday", id="valid-hourofday"),
        pytest.param("dayofweek", id="valid-dayofweek"),
        pytest.param("monthofyear", id="valid-monthofyear"),
    ],
)
def test_validate_rollup_returns_rollup(rollup: object):
    assert validate_rollup(rollup) == rollup


@pytest.mark.parametrize(
    "value,valid",
    [
        pytest.param("2024-01-01", True, id="valid-date"),
        pytest.param("2024-01-01T00:00:00", True, id="valid-datetime"),
        pytest.param("2024-01-01T12:30:45", True, id="valid-datetime-with-time"),
        pytest.param(
            "2024-01-01T12:30:45.123456", True, id="valid-datetime-with-microseconds"
        ),
        pytest.param(
            "2024-01-01T12:30:45+00:00", True, id="valid-datetime-with-utc-offset"
        ),
        pytest.param(
            "2024-01-01T12:30:45-05:00", True, id="valid-datetime-with-negative-offset"
        ),
        pytest.param("2024-01-01T12:30:45Z", True, id="invalid-zulu-time"),
        pytest.param("2024-13-01", False, id="invalid-month"),
        pytest.param("2024-01-32", False, id="invalid-day"),
        pytest.param("2024-02-30", False, id="invalid-feb-30"),
        pytest.param("2024/01/01", False, id="invalid-slashes"),
        pytest.param("01-01-2024", False, id="invalid-format"),
        pytest.param("not a date", False, id="invalid-string"),
        pytest.param("", False, id="empty-string"),
        pytest.param("2024-1-1", False, id="invalid-no-padding"),
        pytest.param(123, False, id="integer"),
        pytest.param(True, False, id="bool-true"),
        pytest.param(False, False, id="bool-false"),
        pytest.param(None, False, id="none"),
        pytest.param([], False, id="empty-list"),
        pytest.param({}, False, id="empty-dict"),
        pytest.param((), False, id="empty-tuple"),
    ],
)
def test_iso8601_check(value: object, valid: bool):
    assert iso8601_check(value) == valid


@pytest.mark.parametrize(
    "value,valid",
    [
        pytest.param("2024-01-01", True, id="valid-date-string"),
        pytest.param("2024-01-01T12:30:45", True, id="valid-datetime-string"),
        pytest.param(datetime.datetime(2024, 1, 1), True, id="valid-datetime-object"),
        pytest.param(
            datetime.datetime(2024, 1, 1, 12, 30, 45),
            True,
            id="valid-datetime-object-with-time",
        ),
        pytest.param("invalid-date", False, id="invalid-string"),
        pytest.param("2024-13-01", False, id="invalid-month-string"),
        pytest.param("", False, id="empty-string"),
        pytest.param(123, False, id="integer"),
        pytest.param(True, False, id="bool-true"),
        pytest.param(False, False, id="bool-false"),
        pytest.param(None, False, id="none"),
        pytest.param([], False, id="empty-list"),
        pytest.param({}, False, id="empty-dict"),
        pytest.param((), False, id="empty-tuple"),
    ],
)
def test_datetime_check(value: object, valid: bool):
    assert datetime_check(value) == valid


@given(st.datetimes())
def test_datetime_check_accepts_datetime_objects(dt: datetime.datetime):
    """Any datetime object should be valid."""
    assert datetime_check(dt) is True


@given(st.dates())
def test_datetime_check_accepts_date_objects(d: datetime.date):
    """Any date object should be valid."""
    dt = datetime.datetime.combine(d, datetime.time())
    assert datetime_check(dt) is True


@given(st.datetimes())
def test_datetime_check_accepts_iso_format_strings(dt: datetime.datetime):
    """ISO format datetime strings should be valid."""
    iso_string = dt.isoformat()
    assert datetime_check(iso_string) is True


@given(st.dates())
def test_datetime_check_accepts_date_strings(d: datetime.date):
    """ISO format date strings (YYYY-MM-DD) should be valid."""
    date_string = d.isoformat()
    assert datetime_check(date_string) is True


@given(
    st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.booleans(),
        st.none(),
        st.lists(st.integers()),
        st.dictionaries(st.text(), st.integers()),
        st.tuples(),
    )
)
def test_datetime_check_rejects_non_datetime_types(value):
    """Non-datetime types should be rejected."""
    assert datetime_check(value) is False


@pytest.mark.parametrize(
    "value,expected",
    [
        pytest.param(
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 1, 1),
            id="datetime-object-unchanged",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 1, 12, 30, 45),
            datetime.datetime(2024, 1, 1, 12, 30, 45),
            id="datetime-object-with-time-unchanged",
        ),
        pytest.param(
            "2024-01-01", datetime.datetime(2024, 1, 1), id="date-string-converted"
        ),
        pytest.param(
            "2024-01-01T12:30:45",
            datetime.datetime(2024, 1, 1, 12, 30, 45),
            id="datetime-string-converted",
        ),
        pytest.param(
            "2024-01-01T12:30:45.123456",
            datetime.datetime(2024, 1, 1, 12, 30, 45, 123456),
            id="datetime-string-with-microseconds-converted",
        ),
    ],
)
def test_to_datetime(value: datetime.datetime | str, expected: datetime.datetime):
    assert to_datetime(value) == expected


@pytest.mark.parametrize(
    "datetime_from,datetime_to,expected_from,expected_to",
    [
        pytest.param(
            "2024-01-01",
            "2024-12-31",
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 12, 31),
            id="both-strings",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 12, 31),
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 12, 31),
            id="both-datetime-objects",
        ),
        pytest.param(
            "2024-01-01",
            datetime.datetime(2024, 12, 31),
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 12, 31),
            id="mixed-string-and-datetime",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 1),
            "2024-12-31",
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 12, 31),
            id="mixed-datetime-and-string",
        ),
        pytest.param(
            "2024-01-01T12:30:45",
            "2024-12-31T23:59:59",
            datetime.datetime(2024, 1, 1, 12, 30, 45),
            datetime.datetime(2024, 12, 31, 23, 59, 59),
            id="datetime-strings-with-time",
        ),
    ],
)
def test_validate_datetime_params_with_both(
    datetime_from: object,
    datetime_to: object,
    expected_from: datetime.datetime,
    expected_to: datetime.datetime,
):
    result_from, result_to = validate_datetime_params(datetime_from, datetime_to)
    assert result_from == expected_from
    assert result_to == expected_to


@pytest.mark.parametrize(
    "datetime_from,expected_from",
    [
        pytest.param(
            "2024-01-01", datetime.datetime(2024, 1, 1), id="string-only-from"
        ),
        pytest.param(
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 1, 1),
            id="datetime-object-only-from",
        ),
        pytest.param(
            "2024-01-01T12:30:45",
            datetime.datetime(2024, 1, 1, 12, 30, 45),
            id="datetime-string-with-time-only-from",
        ),
    ],
)
def test_validate_datetime_params_from_only(
    datetime_from: object, expected_from: datetime.datetime
):
    result_from, result_to = validate_datetime_params(datetime_from, None)
    assert result_from == expected_from
    assert result_to is None


@pytest.mark.parametrize(
    "datetime_from,datetime_to",
    [
        pytest.param("invalid-date", "2024-12-31", id="invalid-from-string"),
        pytest.param("2024-01-01", "invalid-date", id="invalid-to-string"),
        pytest.param("invalid", "also-invalid", id="both-invalid-strings"),
        pytest.param(123, "2024-12-31", id="invalid-from-integer"),
        pytest.param("2024-01-01", 123, id="invalid-to-integer"),
        pytest.param(None, "2024-12-31", id="none-from"),
        pytest.param(True, False, id="bool-values"),
        pytest.param([], {}, id="invalid-types"),
    ],
)
def test_validate_datetime_params_throws_with_both(
    datetime_from: object, datetime_to: object
):
    with pytest.raises(Exception):
        validate_datetime_params(datetime_from, datetime_to)


@pytest.mark.parametrize(
    "datetime_from",
    [
        pytest.param("invalid-date", id="invalid-from-string"),
        pytest.param(123, id="invalid-from-integer"),
        pytest.param(None, id="none-from"),
        pytest.param(True, id="bool-true"),
        pytest.param([], id="empty-list"),
    ],
)
def test_validate_datetime_params_throws_from_only(datetime_from: object):
    with pytest.raises(Exception):
        validate_datetime_params(datetime_from, None)


@pytest.mark.parametrize(
    "parameter_type,valid",
    [
        pytest.param("pollutant", True, id="valid-pollutant"),
        pytest.param("meteorological", True, id="valid-meteorological"),
        pytest.param("Pollutant", False, id="invalid-uppercase"),
        pytest.param("METEOROLOGICAL", False, id="invalid-all-caps"),
        pytest.param("Meteorological", False, id="invalid-mixed-case"),
        pytest.param("pollution", False, id="invalid-similar-word"),
        pytest.param("", False, id="empty-string"),
        pytest.param("invalid", False, id="invalid-string"),
        pytest.param(123, False, id="integer"),
        pytest.param(True, False, id="bool-true"),
        pytest.param(False, False, id="bool-false"),
        pytest.param(None, False, id="none"),
        pytest.param([], False, id="empty-list"),
        pytest.param({}, False, id="empty-dict"),
        pytest.param((), False, id="empty-tuple"),
    ],
)
def test_parameter_type_check(parameter_type: object, valid: bool):
    assert parameter_type_check(parameter_type) == valid
