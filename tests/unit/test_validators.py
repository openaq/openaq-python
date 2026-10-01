import datetime

import pytest
from freezegun import freeze_time
from hypothesis import given
from hypothesis import strategies as st

from openaq.core.constants import ISO_CODES, MAX_LIMIT
from openaq.core.exceptions import (
    IdentifierOutOfBoundsError,
    InvalidParameterError,
)
from openaq.core.types import Data
from openaq.core.validators import (
    countries_id_iso_exclusivity_check,
    data_check,
    date_from_lesser_check,
    datetime_check,
    datetime_date_params_exclusivity_check,
    datetime_from_lesser_check,
    datetime_timezone_consistency_check,
    geospatial_params_exclusivity_check,
    integer_id_check,
    is_int_list,
    iso8601_date_check,
    iso8601_datetime_check,
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
    validate_data_rollup_compatibility,
    validate_datetime_params,
    validate_geospatial_params,
    validate_integer_id,
    validate_iso_param,
    validate_limit_param,
    validate_mobile,
    validate_monitor,
    validate_order_by,
    validate_page_param,
    validate_parameter_type,
    validate_radius,
    validate_rollup,
    validate_sort_order,
)

MAX_ID = 2**31 - 1

DATA_VALUES = ("measurements", "hours", "days", "years")
ROLLUP_VALUES = (
    "hourly",
    "daily",
    "monthly",
    "yearly",
    "hourofday",
    "dayofweek",
    "monthofyear",
)
PARAMETER_TYPE_VALUES = ("pollutant", "meteorological")
SORT_ORDER_VALUES = ("ASC", "DESC", "asc", "desc")

ANY_VALUE = st.one_of(
    st.integers(),
    st.floats(),
    st.booleans(),
    st.text(),
    st.none(),
    st.lists(st.integers()),
    st.dictionaries(st.text(), st.integers()),
)

NOT_INTEGERS = ANY_VALUE.filter(lambda v: not isinstance(v, int) or isinstance(v, bool))
NOT_STRINGS = ANY_VALUE.filter(lambda v: not isinstance(v, str))

LATITUDES = st.floats(-90, 90) | st.integers(-90, 90)
LONGITUDES = st.floats(-180, 180) | st.integers(-180, 180)

OUT_OF_RANGE_LATITUDES = st.floats(allow_nan=False).filter(lambda x: abs(x) > 90)
OUT_OF_RANGE_LONGITUDES = st.floats(allow_nan=False).filter(lambda x: abs(x) > 180)

NAIVE_OR_UTC_DATETIMES = st.datetimes(timezones=st.none() | st.just(datetime.UTC))


def values_near(valid):
    variants = sorted(
        {form for v in valid for form in (v, v.upper(), v.lower(), v.capitalize())}
    )
    return st.sampled_from(variants) | ANY_VALUE


def is_one_of(valid):
    return lambda v: isinstance(v, str) and v in valid


def is_iso_code(value):
    return isinstance(value, str) and len(value) == 2 and value.upper() in ISO_CODES


def ordered_pair(values):
    return st.lists(values, min_size=2, max_size=2, unique=True).map(sorted)



@pytest.mark.parametrize(
    ("check", "low", "high"),
    [
        pytest.param(integer_id_check, 1, MAX_ID, id="integer-id"),
        pytest.param(radius_check, 1, 25_000, id="radius"),
        pytest.param(page_check, 1, None, id="page"),
        pytest.param(limit_check, 1, MAX_LIMIT, id="limit"),
    ],
)
@given(data=st.data())
def test_range_check_accepts_exactly_its_range(check, low, high, data):
    """Integers inside the range pass, everything else fails, including the boundaries."""
    boundaries = [low - 1, low] + ([high, high + 1] if high is not None else [])
    value = data.draw(st.integers() | st.sampled_from(boundaries))
    in_range = value >= low and (high is None or value <= high)
    assert check(value) == in_range


@pytest.mark.parametrize(
    "check",
    [
        pytest.param(integer_id_check, id="integer-id"),
        pytest.param(radius_check, id="radius"),
        pytest.param(page_check, id="page"),
        pytest.param(limit_check, id="limit"),
    ],
)
@given(value=NOT_INTEGERS)
def test_range_check_rejects_non_integers(check, value):
    """Booleans, floats, strings, and other types are never valid integers."""
    assert not check(value)


@given(st.lists(st.integers() | st.sampled_from([0, 1, MAX_ID, MAX_ID + 1])))
def test_is_int_list_accepts_only_valid_ids(values):
    assert is_int_list(values) == all(1 <= v <= MAX_ID for v in values)


@given(st.lists(st.integers(1, MAX_ID)), NOT_INTEGERS)
def test_is_int_list_rejects_any_non_integer(valid_ids, invalid):
    assert not is_int_list([*valid_ids, invalid])



@pytest.mark.parametrize(
    ("check", "is_valid", "values"),
    [
        pytest.param(
            data_check, is_one_of(DATA_VALUES), values_near(DATA_VALUES), id="data"
        ),
        pytest.param(
            rollup_check,
            is_one_of(ROLLUP_VALUES),
            values_near(ROLLUP_VALUES),
            id="rollup",
        ),
        pytest.param(
            parameter_type_check,
            is_one_of(PARAMETER_TYPE_VALUES),
            values_near(PARAMETER_TYPE_VALUES),
            id="parameter-type",
        ),
        pytest.param(iso_check, is_iso_code, values_near(ISO_CODES), id="iso"),
    ],
)
@given(data=st.data())
def test_check_accepts_exactly_valid_values(check, is_valid, values, data):
    """Only the documented values pass, with the documented case sensitivity."""
    value = data.draw(values)
    assert check(value) == is_valid(value)


@pytest.mark.parametrize(
    ("validate", "is_valid", "error", "values"),
    [
        pytest.param(
            validate_integer_id,
            integer_id_check,
            IdentifierOutOfBoundsError,
            ANY_VALUE,
            id="integer-id",
        ),
        pytest.param(
            validate_radius, radius_check, InvalidParameterError, ANY_VALUE, id="radius"
        ),
        pytest.param(
            validate_page_param, page_check, InvalidParameterError, ANY_VALUE, id="page"
        ),
        pytest.param(
            validate_limit_param,
            limit_check,
            InvalidParameterError,
            ANY_VALUE,
            id="limit",
        ),
        pytest.param(
            validate_iso_param,
            iso_check,
            InvalidParameterError,
            values_near(ISO_CODES),
            id="iso",
        ),
        pytest.param(
            validate_data,
            data_check,
            InvalidParameterError,
            values_near(DATA_VALUES),
            id="data",
        ),
        pytest.param(
            validate_rollup,
            rollup_check,
            InvalidParameterError,
            values_near(ROLLUP_VALUES),
            id="rollup",
        ),
        pytest.param(
            validate_parameter_type,
            parameter_type_check,
            InvalidParameterError,
            values_near(PARAMETER_TYPE_VALUES),
            id="parameter-type",
        ),
        pytest.param(
            validate_monitor,
            lambda v: isinstance(v, bool),
            InvalidParameterError,
            ANY_VALUE,
            id="monitor",
        ),
        pytest.param(
            validate_mobile,
            lambda v: isinstance(v, bool),
            InvalidParameterError,
            ANY_VALUE,
            id="mobile",
        ),
        pytest.param(
            validate_order_by,
            lambda v: isinstance(v, str),
            InvalidParameterError,
            ANY_VALUE,
            id="order-by",
        ),
        pytest.param(
            validate_sort_order,
            is_one_of(SORT_ORDER_VALUES),
            InvalidParameterError,
            values_near(SORT_ORDER_VALUES),
            id="sort-order",
        ),
    ],
)
@given(data=st.data())
def test_validator_accepts_exactly_valid_values(validate, is_valid, error, values, data):
    """Valid values are returned unchanged; anything else raises the documented error."""
    value = data.draw(values)
    if is_valid(value):
        assert validate(value) == value
    else:
        with pytest.raises(error):
            validate(value)


# Coordinates


@given(LATITUDES, LONGITUDES)
def test_validate_coordinates_accepts_in_range(lat, lon):
    assert validate_coordinates((lat, lon)) == (lat, lon)


@given(OUT_OF_RANGE_LATITUDES, LONGITUDES)
def test_validate_coordinates_rejects_latitude_out_of_range(lat, lon):
    with pytest.raises(InvalidParameterError):
        validate_coordinates((lat, lon))


@given(LATITUDES, OUT_OF_RANGE_LONGITUDES)
def test_validate_coordinates_rejects_longitude_out_of_range(lat, lon):
    with pytest.raises(InvalidParameterError):
        validate_coordinates((lat, lon))


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
        pytest.param(("-18.9185", "47.5211"), id="all-string-elements"),
        pytest.param((-18.9185, "47.5211"), id="mixed-string-element"),
        pytest.param((None, 47.5211), id="none-in-first-position"),
        pytest.param((-18.9185, None), id="none-in-second-position"),
    ],
)
def test_validate_coordinates_rejects_wrong_shape(coordinates):
    with pytest.raises(InvalidParameterError):
        validate_coordinates(coordinates)


# Bounding boxes


@given(ordered_pair(LONGITUDES), ordered_pair(LATITUDES))
def test_validate_bbox_accepts_ordered_bounds(lons, lats):
    bbox = (lons[0], lats[0], lons[1], lats[1])
    assert validate_bbox(bbox) == bbox


@given(ordered_pair(LONGITUDES), ordered_pair(LATITUDES))
def test_validate_bbox_rejects_swapped_longitudes(lons, lats):
    with pytest.raises(InvalidParameterError):
        validate_bbox((lons[1], lats[0], lons[0], lats[1]))


@given(ordered_pair(LONGITUDES), ordered_pair(LATITUDES))
def test_validate_bbox_rejects_swapped_latitudes(lons, lats):
    with pytest.raises(InvalidParameterError):
        validate_bbox((lons[0], lats[1], lons[1], lats[0]))


@given(ordered_pair(LONGITUDES), OUT_OF_RANGE_LATITUDES)
def test_validate_bbox_rejects_latitude_out_of_range(lons, lat):
    with pytest.raises(InvalidParameterError):
        validate_bbox((lons[0], lat, lons[1], 0.0))


@given(OUT_OF_RANGE_LONGITUDES, ordered_pair(LATITUDES))
def test_validate_bbox_rejects_longitude_out_of_range(lon, lats):
    with pytest.raises(InvalidParameterError):
        validate_bbox((lon, lats[0], 0.0, lats[1]))


@pytest.mark.parametrize(
    "bbox",
    [
        pytest.param(None, id="none-value"),
        pytest.param("44.2,40.1,44.8,40.2", id="string-instead-of-tuple"),
        pytest.param([44.2, 40.1, 44.8, 40.2], id="list-instead-of-tuple"),
        pytest.param({"min_lon": 44.2, "min_lat": 40.1}, id="dict-instead-of-tuple"),
        pytest.param(42, id="single-number-instead-of-tuple"),
        pytest.param((), id="empty-tuple"),
        pytest.param((44.2,), id="tuple-with-one-element"),
        pytest.param((44.2, 40.1, 44.8), id="tuple-with-three-elements"),
        pytest.param((44.2, 40.1, 44.8, 40.2, 0), id="tuple-with-five-elements"),
        pytest.param(("44.2", "40.1", "44.8", "40.2"), id="all-string-elements"),
        pytest.param((44.2, 40.1, "44.8", 40.2), id="one-string-element"),
        pytest.param((None, 40.1, 44.8, 40.2), id="none-in-first-position"),
        pytest.param((44.2, 40.1, 44.2, 40.2), id="min-lon-equals-max-lon"),
        pytest.param((44.2, 40.1, 44.8, 40.1), id="min-lat-equals-max-lat"),
    ],
)
def test_validate_bbox_rejects_wrong_shape(bbox):
    with pytest.raises(InvalidParameterError):
        validate_bbox(bbox)


# Parameter combinations


@pytest.mark.parametrize(
    "countries_id,iso,valid",
    [
        pytest.param(42, "US", False, id="both-values-provided"),
        pytest.param(42, None, True, id="only-countries_id-provided"),
        pytest.param(None, "US", True, id="only-iso-provided"),
        pytest.param(None, None, True, id="neither-provided"),
    ],
)
def test_countries_id_iso_exclusivity_check(countries_id: int, iso: str, valid: bool):
    assert countries_id_iso_exclusivity_check(countries_id, iso) == valid


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
            None,
            1000,
            None,
            "radius requires coordinates parameter",
            id="radius-without-coordinates",
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
        pytest.param((91.0, 0.0), 1000, None, id="invalid-coordinates-out-of-range"),
        pytest.param((0.0, 0.0), 0, None, id="invalid-radius-zero"),
        pytest.param((0.0, 0.0), "1000", None, id="invalid-radius-string"),
        pytest.param(None, None, "invalid", id="invalid-bbox-string"),
        pytest.param(None, None, (1.0, 0.0, 0.0, 1.0), id="invalid-bbox-inverted"),
    ],
)
def test_validate_geospatial_params_throws_validation_errors(coordinates, radius, bbox):
    """Invalid values are caught by the coordinate, radius, and bbox validators."""
    with pytest.raises(InvalidParameterError):
        validate_geospatial_params(coordinates, radius, bbox)


@pytest.mark.parametrize(
    "data,rollup",
    [
        pytest.param("measurements", None, id="measurements-no-rollup"),
        pytest.param("measurements", "hourly", id="measurements-hourly"),
        pytest.param("measurements", "daily", id="measurements-daily"),
        pytest.param("hours", None, id="hours-no-rollup"),
        pytest.param("hours", "daily", id="hours-daily"),
        pytest.param("hours", "monthly", id="hours-monthly"),
        pytest.param("hours", "yearly", id="hours-yearly"),
        pytest.param("hours", "hourofday", id="hours-hourofday"),
        pytest.param("hours", "dayofweek", id="hours-dayofweek"),
        pytest.param("hours", "monthofyear", id="hours-monthofyear"),
        pytest.param("days", None, id="days-no-rollup"),
        pytest.param("days", "monthly", id="days-monthly"),
        pytest.param("days", "yearly", id="days-yearly"),
        pytest.param("days", "dayofweek", id="days-dayofweek"),
        pytest.param("days", "monthofyear", id="days-monthofyear"),
        pytest.param("years", None, id="years-no-rollup"),
    ],
)
def test_validate_data_rollup_compatibility_valid(data: str, rollup: str | None):
    """Valid data and rollup combinations succeed."""
    validated_data, validated_rollup = validate_data_rollup_compatibility(data, rollup)
    assert validated_data == data
    assert validated_rollup == rollup


@pytest.mark.parametrize(
    "data,rollup",
    [
        pytest.param("measurements", "monthly", id="measurements-monthly"),
        pytest.param("measurements", "yearly", id="measurements-yearly"),
        pytest.param("measurements", "hourofday", id="measurements-hourofday"),
        pytest.param("measurements", "dayofweek", id="measurements-dayofweek"),
        pytest.param("measurements", "monthofyear", id="measurements-monthofyear"),
        pytest.param("hours", "hourly", id="hours-hourly"),
        pytest.param("days", "hourly", id="days-hourly"),
        pytest.param("days", "daily", id="days-daily"),
        pytest.param("days", "hourofday", id="days-hourofday"),
        pytest.param("years", "hourly", id="years-hourly"),
        pytest.param("years", "daily", id="years-daily"),
        pytest.param("years", "monthly", id="years-monthly"),
        pytest.param("years", "yearly", id="years-yearly"),
        pytest.param("years", "hourofday", id="years-hourofday"),
        pytest.param("years", "dayofweek", id="years-dayofweek"),
        pytest.param("years", "monthofyear", id="years-monthofyear"),
    ],
)
def test_validate_data_rollup_compatibility_invalid_combination_throws(
    data: str, rollup: str
):
    with pytest.raises(InvalidParameterError):
        validate_data_rollup_compatibility(data, rollup)


@pytest.mark.parametrize(
    "datetime_from, datetime_to, date_from, date_to, valid",
    [
        pytest.param(
            datetime.datetime(2026, 1, 1),
            datetime.datetime(2026, 1, 2),
            None,
            None,
            True,
            id="both_datetime_params_only",
        ),
        pytest.param(
            datetime.datetime(2026, 1, 1), None, None, None, True, id="only_datetime_from"
        ),
        pytest.param(
            None, datetime.datetime(2026, 1, 2), None, None, True, id="only_datetime_to"
        ),
        pytest.param(
            None,
            None,
            datetime.date(2026, 1, 1),
            datetime.date(2026, 1, 2),
            True,
            id="both_date_params_only",
        ),
        pytest.param(
            None, None, datetime.date(2026, 1, 1), None, True, id="only_date_from"
        ),
        pytest.param(None, None, None, datetime.date(2026, 1, 2), True, id="only_date_to"),
        pytest.param(None, None, None, None, True, id="all_none"),
        pytest.param(
            datetime.datetime(2026, 1, 1),
            None,
            datetime.date(2026, 1, 1),
            None,
            False,
            id="datetime_from_and_date_from_mixed",
        ),
        pytest.param(
            datetime.datetime(2026, 1, 1),
            None,
            None,
            datetime.date(2026, 1, 2),
            False,
            id="datetime_from_and_date_to_mixed",
        ),
        pytest.param(
            None,
            datetime.datetime(2026, 1, 2),
            datetime.date(2026, 1, 1),
            None,
            False,
            id="datetime_to_and_date_from_mixed",
        ),
        pytest.param(
            None,
            datetime.datetime(2026, 1, 2),
            None,
            datetime.date(2026, 1, 2),
            False,
            id="datetime_to_and_date_to_mixed",
        ),
        pytest.param(
            datetime.datetime(2026, 1, 1),
            datetime.datetime(2026, 1, 2),
            datetime.date(2026, 1, 1),
            datetime.date(2026, 1, 2),
            False,
            id="all_params_mixed",
        ),
    ],
)
def test_datetime_date_params_exclusivity_check(
    datetime_from, datetime_to, date_from, date_to, valid
):
    assert (
        datetime_date_params_exclusivity_check(
            datetime_from, datetime_to, date_from, date_to
        )
        == valid
    )


# Date and datetime strings


@pytest.mark.parametrize(
    "check",
    [
        pytest.param(iso8601_datetime_check, id="iso8601-datetime"),
        pytest.param(iso8601_date_check, id="iso8601-date"),
        pytest.param(datetime_check, id="datetime"),
    ],
)
@given(value=NOT_STRINGS)
def test_date_checks_reject_non_strings(check, value):
    assert not check(value)


@given(NAIVE_OR_UTC_DATETIMES)
def test_datetime_isoformat_round_trips(value):
    """Any datetime written with isoformat() is accepted and parsed back unchanged."""
    assert iso8601_datetime_check(value.isoformat())
    assert to_datetime(value.isoformat()) == value


@given(st.dates())
def test_date_isoformat_is_accepted(value):
    assert iso8601_date_check(value.isoformat())


@pytest.mark.parametrize(
    "value,valid",
    [
        pytest.param("2024-01-01", True, id="valid-date"),
        pytest.param("2024-01-01T12:30:45-05:00", True, id="valid-negative-offset"),
        pytest.param("2024-01-01T12:30:45Z", True, id="valid-zulu-time"),
        pytest.param("2024-13-01", False, id="invalid-month"),
        pytest.param("2024-01-32", False, id="invalid-day"),
        pytest.param("2024-02-30", False, id="invalid-feb-30"),
        pytest.param("2023-02-29", False, id="invalid-non-leap-year-feb-29"),
        pytest.param("2024/01/01", False, id="invalid-slashes"),
        pytest.param("01-01-2024", False, id="invalid-format"),
        pytest.param("not a date", False, id="invalid-string"),
        pytest.param("", False, id="empty-string"),
        pytest.param("2024-1-1", False, id="invalid-no-padding"),
    ],
)
def test_iso8601_datetime_check(value: str, valid: bool):
    assert iso8601_datetime_check(value) == valid


@pytest.mark.parametrize(
    "value,valid",
    [
        pytest.param("2024-02-29", True, id="valid-leap-year"),
        pytest.param("2024-01-01T00:00:00", False, id="invalid-datetime-with-time"),
        pytest.param("2024-01-01T12:30:45+00:00", False, id="invalid-utc-offset"),
        pytest.param("2024-01-01T12:30:45Z", False, id="invalid-zulu-time"),
        pytest.param("2024-13-01", False, id="invalid-month"),
        pytest.param("2023-02-29", False, id="invalid-non-leap-year-feb-29"),
        pytest.param("2024/01/01", False, id="invalid-slashes"),
        pytest.param("01-01-2024", False, id="invalid-format"),
        pytest.param("not a date", False, id="invalid-string"),
        pytest.param("", False, id="empty-string"),
        pytest.param("2024-1-1", False, id="invalid-no-padding"),
        pytest.param("24-01-01", False, id="invalid-two-digit-year"),
    ],
)
def test_iso8601_date_check(value: str, valid: bool):
    assert iso8601_date_check(value) == valid


@pytest.mark.parametrize(
    "value,valid",
    [
        pytest.param("2024-01-01", True, id="valid-date-string"),
        pytest.param("2024-01-01T12:30:45", True, id="valid-datetime-string"),
        pytest.param(datetime.datetime(2024, 1, 1), True, id="valid-datetime-object"),
        pytest.param("invalid-date", False, id="invalid-string"),
        pytest.param("2024-13-01", False, id="invalid-month-string"),
        pytest.param("", False, id="empty-string"),
    ],
)
def test_datetime_check(value: object, valid: bool):
    assert datetime_check(value) == valid


@pytest.mark.parametrize(
    "value,expected",
    [
        pytest.param(
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 1, 1),
            id="datetime-object-unchanged",
        ),
        pytest.param(
            "2024-01-01", datetime.datetime(2024, 1, 1), id="date-string-converted"
        ),
        pytest.param(
            "2024-01-01T12:30:45Z",
            datetime.datetime(2024, 1, 1, 12, 30, 45, tzinfo=datetime.UTC),
            id="utc-string-converted",
        ),
    ],
)
def test_to_datetime(value: datetime.datetime | str, expected: datetime.datetime):
    assert to_datetime(value) == expected


# Date and datetime ordering


@pytest.mark.parametrize(
    "datetime_from,datetime_to,frozen_time,expected",
    [
        pytest.param(
            datetime.datetime(2024, 1, 1, 12),
            datetime.datetime(2024, 1, 2, 12),
            None,
            True,
            id="from_before_to",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 2, 12),
            datetime.datetime(2024, 1, 1, 12),
            None,
            False,
            id="from_after_to",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 1, 12),
            datetime.datetime(2024, 1, 1, 12),
            None,
            False,
            id="equal_datetimes",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 1, 12, 0, 0, 0),
            datetime.datetime(2024, 1, 1, 12, 0, 0, 1),
            None,
            True,
            id="microsecond_difference",
        ),
        pytest.param(
            datetime.datetime.min, datetime.datetime(2024, 1, 1), None, True, id="min_datetime"
        ),
        pytest.param(
            datetime.datetime.max, datetime.datetime(2024, 1, 1), None, False, id="max_datetime"
        ),
        pytest.param(
            datetime.datetime(2024, 1, 14, 12),
            None,
            "2024-01-15 12:00:00",
            True,
            id="past_vs_now",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 16, 12),
            None,
            "2024-01-15 12:00:00",
            False,
            id="future_vs_now",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 15, 12),
            None,
            "2024-01-15 12:00:00",
            False,
            id="equal_to_now",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 15, 11, 59, 59, 999999),
            None,
            "2024-01-15 12:00:00",
            True,
            id="microsecond_before_now",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 14, 12, tzinfo=datetime.UTC),
            None,
            "2024-01-15 12:00:00",
            True,
            id="utc_past_vs_now",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 16, 12, tzinfo=datetime.UTC),
            None,
            "2024-01-15 12:00:00",
            False,
            id="utc_future_vs_now",
        ),
    ],
)
def test_datetime_from_lesser_check(datetime_from, datetime_to, frozen_time, expected):
    if frozen_time:
        with freeze_time(frozen_time):
            assert datetime_from_lesser_check(datetime_from, datetime_to) == expected
    else:
        assert datetime_from_lesser_check(datetime_from, datetime_to) == expected


@pytest.mark.parametrize(
    "date_from,date_to,frozen_time,expected",
    [
        pytest.param(
            datetime.date(2024, 1, 1), datetime.date(2024, 1, 2), None, True, id="from_before_to"
        ),
        pytest.param(
            datetime.date(2024, 1, 2), datetime.date(2024, 1, 1), None, False, id="from_after_to"
        ),
        pytest.param(
            datetime.date(2024, 1, 1), datetime.date(2024, 1, 1), None, False, id="equal_dates"
        ),
        pytest.param(datetime.date.min, datetime.date(2024, 1, 1), None, True, id="min_date"),
        pytest.param(datetime.date.max, datetime.date(2024, 1, 1), None, False, id="max_date"),
        pytest.param(datetime.date(2024, 1, 14), None, "2024-01-15", True, id="past_vs_today"),
        pytest.param(datetime.date(2024, 1, 16), None, "2024-01-15", False, id="future_vs_today"),
        pytest.param(datetime.date(2024, 1, 15), None, "2024-01-15", False, id="equal_to_today"),
        pytest.param(
            datetime.date(2024, 2, 28), datetime.date(2024, 2, 29), None, True, id="leap_year_feb_28_29"
        ),
        pytest.param(
            datetime.date(2023, 12, 31), datetime.date(2024, 1, 1), None, True, id="year_boundary"
        ),
    ],
)
def test_date_from_lesser_check(date_from, date_to, frozen_time, expected):
    if frozen_time:
        with freeze_time(frozen_time):
            assert date_from_lesser_check(date_from, date_to) == expected
    else:
        assert date_from_lesser_check(date_from, date_to) == expected


@pytest.mark.parametrize(
    "datetime_from,datetime_to,valid",
    [
        pytest.param(
            datetime.datetime(2024, 1, 1), datetime.datetime(2024, 1, 2), True, id="both-naive"
        ),
        pytest.param(
            datetime.datetime(2024, 1, 1, tzinfo=datetime.UTC),
            datetime.datetime(2024, 1, 2, tzinfo=datetime.UTC),
            True,
            id="both-aware",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 1, tzinfo=datetime.UTC),
            datetime.datetime(2024, 1, 2),
            False,
            id="aware-from-naive-to",
        ),
        pytest.param(
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 1, 2, tzinfo=datetime.UTC),
            False,
            id="naive-from-aware-to",
        ),
    ],
)
def test_datetime_timezone_consistency_check(datetime_from, datetime_to, valid):
    assert datetime_timezone_consistency_check(datetime_from, datetime_to) == valid


# Full date and datetime parameter validation


@given(NAIVE_OR_UTC_DATETIMES, st.none() | NAIVE_OR_UTC_DATETIMES)
def test_validate_datetime_params_only_raises_invalid_parameter_error(
    datetime_from, datetime_to
):
    """Any combination of naive and UTC datetimes either validates or raises InvalidParameterError."""
    try:
        validate_datetime_params("measurements", datetime_from, datetime_to, None, None)
    except InvalidParameterError:
        pass


@pytest.mark.parametrize(
    "data,datetime_from,datetime_to,date_from,date_to,expected",
    [
        pytest.param(
            "measurements",
            "2024-01-01",
            "2024-12-31",
            None,
            None,
            (datetime.datetime(2024, 1, 1), datetime.datetime(2024, 12, 31), None, None),
            id="measurements-both-datetime-strings",
        ),
        pytest.param(
            "hours",
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 12, 31),
            None,
            None,
            (datetime.datetime(2024, 1, 1), datetime.datetime(2024, 12, 31), None, None),
            id="hours-both-datetime-objects",
        ),
        pytest.param(
            "measurements",
            "2024-01-01",
            datetime.datetime(2024, 12, 31),
            None,
            None,
            (datetime.datetime(2024, 1, 1), datetime.datetime(2024, 12, 31), None, None),
            id="measurements-mixed-string-and-datetime",
        ),
        pytest.param(
            "days",
            None,
            None,
            "2024-01-01",
            "2024-12-31",
            (None, None, datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)),
            id="days-both-date-strings",
        ),
        pytest.param(
            "years",
            None,
            None,
            datetime.date(2024, 1, 1),
            datetime.date(2024, 12, 31),
            (None, None, datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)),
            id="years-both-date-objects",
        ),
        pytest.param(
            "days",
            None,
            None,
            "2024-01-01",
            datetime.date(2024, 12, 31),
            (None, None, datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)),
            id="days-mixed-string-and-date",
        ),
    ],
)
def test_validate_datetime_params_with_both(
    data: Data, datetime_from, datetime_to, date_from, date_to, expected
):
    result = validate_datetime_params(data, datetime_from, datetime_to, date_from, date_to)
    assert result == expected


@pytest.mark.parametrize(
    "data,datetime_from,date_from,expected",
    [
        pytest.param(
            "measurements",
            "2024-01-01",
            None,
            (datetime.datetime(2024, 1, 1), None, None, None),
            id="measurements-string-only-from",
        ),
        pytest.param(
            "hours",
            datetime.datetime(2024, 1, 1),
            None,
            (datetime.datetime(2024, 1, 1), None, None, None),
            id="hours-datetime-object-only-from",
        ),
        pytest.param(
            "measurements",
            "2024-01-01T00:00:00Z",
            None,
            (datetime.datetime(2024, 1, 1, tzinfo=datetime.UTC), None, None, None),
            id="measurements-utc-string-only-from",
        ),
        pytest.param(
            "days",
            None,
            "2024-01-01",
            (None, None, datetime.date(2024, 1, 1), None),
            id="days-string-only-from",
        ),
        pytest.param(
            "years",
            None,
            datetime.date(2024, 1, 1),
            (None, None, datetime.date(2024, 1, 1), None),
            id="years-date-object-only-from",
        ),
    ],
)
def test_validate_datetime_params_from_only(data: Data, datetime_from, date_from, expected):
    result = validate_datetime_params(data, datetime_from, None, date_from, None)
    assert result == expected


@pytest.mark.parametrize(
    "data,datetime_from,datetime_to,date_from,date_to",
    [
        pytest.param(
            "measurements", "invalid-date", "2024-12-31", None, None, id="measurements-invalid-from-string"
        ),
        pytest.param("hours", "2024-01-01", "invalid-date", None, None, id="hours-invalid-to-string"),
        pytest.param("hours", 123, "2024-12-31", None, None, id="hours-invalid-from-integer"),
        pytest.param("hours", True, False, None, None, id="hours-bool-values"),
        pytest.param("measurements", [], {}, None, None, id="measurements-invalid-types"),
        pytest.param("hours", "2025-12-31", "2025-01-01", None, None, id="hours-from-after-to"),
        pytest.param(
            "measurements", "2025-01-01", "2025-01-01", None, None, id="measurements-from-equals-to"
        ),
        pytest.param(
            "measurements",
            "2024-01-01T00:00:00Z",
            "2024-02-01T00:00:00",
            None,
            None,
            id="measurements-mixed-timezone-awareness",
        ),
        pytest.param("days", None, None, "invalid-date", "2024-12-31", id="days-invalid-from-string"),
        pytest.param("years", None, None, "2024-01-01", 123, id="years-invalid-to-integer"),
        pytest.param("days", None, None, "2025-12-31", "2025-01-01", id="days-from-after-to"),
        pytest.param("years", None, None, "2025-01-01", "2025-01-01", id="years-from-equals-to"),
        pytest.param(
            "measurements", None, None, "2024-01-01", "2024-12-31", id="measurements-wrong-params-date"
        ),
        pytest.param("hours", None, None, "2024-01-01", None, id="hours-wrong-params-date"),
        pytest.param("days", "2024-01-01", "2024-12-31", None, None, id="days-wrong-params-datetime"),
        pytest.param("years", "2024-01-01", None, None, None, id="years-wrong-params-datetime"),
    ],
)
def test_validate_datetime_params_throws_with_both(
    data: Data, datetime_from, datetime_to, date_from, date_to
):
    with pytest.raises(InvalidParameterError):
        validate_datetime_params(data, datetime_from, datetime_to, date_from, date_to)


@pytest.mark.parametrize(
    "data,datetime_from,date_from",
    [
        pytest.param("measurements", "invalid-date", None, id="measurements-invalid-from-string"),
        pytest.param("hours", 123, None, id="hours-invalid-from-integer"),
        pytest.param("measurements", [], None, id="measurements-invalid-type"),
        pytest.param("days", None, "invalid-date", id="days-invalid-from-string"),
        pytest.param("years", None, 123, id="years-invalid-from-integer"),
        pytest.param("days", None, [], id="days-invalid-type"),
    ],
)
def test_validate_datetime_params_throws_from_only_invalid_type(
    data: Data, datetime_from, date_from
):
    """Invalid types raise InvalidParameterError when the to parameters are None."""
    with pytest.raises(InvalidParameterError):
        validate_datetime_params(data, datetime_from, None, date_from, None)


@freeze_time("2024-01-15 12:00:00")
@pytest.mark.parametrize(
    "data,datetime_from,date_from",
    [
        pytest.param("measurements", "2024-01-16", None, id="measurements-future-string"),
        pytest.param("hours", datetime.datetime(2024, 1, 16), None, id="hours-future-datetime"),
        pytest.param(
            "measurements", "2024-01-16T00:00:00Z", None, id="measurements-future-utc-string"
        ),
        pytest.param("days", None, "2024-01-16", id="days-future-string"),
        pytest.param("years", None, datetime.date(2024, 1, 16), id="years-future-date"),
    ],
)
def test_validate_datetime_params_throws_from_only_future_datetime(
    data: Data, datetime_from, date_from
):
    """Future from parameters raise InvalidParameterError when the to parameters are None."""
    with pytest.raises(InvalidParameterError):
        validate_datetime_params(data, datetime_from, None, date_from, None)


@pytest.mark.parametrize("data", ["measurements", "hours", "days", "years"])
def test_validate_datetime_params_all_none(data: Data):
    """All None parameters return an all None tuple."""
    assert validate_datetime_params(data, None, None, None, None) == (None, None, None, None)
