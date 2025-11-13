"""Validator functions for type checking and runtime validation."""

import datetime
from typing import TypeGuard, cast
from openaq.shared.constants import ISO_CODES, MAX_LIMIT
from openaq.shared.exceptions import (
    IdentifierOutOfBoundsError,
    InvalidParameterError,
)
from openaq.shared.types import (
    _DATA_VALUES,
    _PARAMETER_TYPE_VALUES,
    _ROLLUP_VALUES,
    _SORT_ORDER_VALUES,
    BboxOnly,
    CoordinatesRadius,
    Data,
    ParameterType,
    Rollup,
    SortOrder,
)


def integer_id_check(id: object) -> TypeGuard[int]:
    """Check if value is a valid positive integer within 32-bit range.

    Args:
        id: Value to validate as an API identifier.

    Returns:
        True if value is a valid integer ID (1 to 2,147,483,647), False otherwise.
    """
    if isinstance(id, bool):
        return False
    if not isinstance(id, int):
        return False
    return id > 0 and id < 1 << 31


def validate_integer_id(id: object) -> int:
    """Validate integer ID parameter and raise error if invalid.

    Args:
        id: Value representing an ID query or path parameter.

    Returns:
        The unaltered validated integer ID.

    Raises:
        IdentifierOutOfBoundsError: If ID is not a positive integer within valid range.
    """
    if not integer_id_check(id):
        message = f"ID values must be between 1 and {1 << 31 - 1}, got {id}"
        raise IdentifierOutOfBoundsError(message)
    return id


def radius_check(radius: object) -> TypeGuard[int]:
    """Check if value is a valid radius integer.

    Args:
        radius: Value to validate as a radius query parameter.

    Returns:
        True if value is an integer between 1 and 25,000 (meters), False otherwise.
    """
    if isinstance(radius, bool):
        return False
    if not (isinstance(radius, int)):
        return False
    return 1 <= radius <= 25_000


def validate_radius(radius: object) -> int:
    """Validate radius query parameter and raise error if invalid.

    Args:
        radius: Value representing the radius query parameter (in meters).

    Returns:
        The unaltered validated radius integer.

    Raises:
        InvalidParameterError: If radius is not an integer between 1 and 25,000.
    """
    if not radius_check(radius):
        raise InvalidParameterError(
            f"Radius must be an integer greater than zero and less that 25,000 (25km)"
        )
    return radius


def validate_coordinates(coordinates: object) -> tuple[float, float]:
    """Validate coordinates query parameter and raise error if invalid.

    Args:
        coordinates: Value representing the coordinates query parameter as (latitude, longitude).

    Returns:
        The unaltered validated coordinates tuple.

    Raises:
        InvalidParameterError: If coordinates are not a valid (lat, lon) tuple with valid ranges.
    """
    if not isinstance(coordinates, tuple):
        raise InvalidParameterError(
            f"Coordinates must be a tuple, got {type(coordinates).__name__}"
        )

    if len(coordinates) != 2:
        raise InvalidParameterError(
            f"Coordinates must have exactly 2 values, got {len(coordinates)}"
        )

    if not all(isinstance(x, (int, float)) for x in coordinates):
        raise InvalidParameterError("Coordinates must contain only numbers")

    lat, lon = coordinates

    if not -90 <= lat <= 90:
        raise InvalidParameterError(f"Latitude must be between -90 and 90, got {lat}")

    if not -180 <= lon <= 180:
        raise InvalidParameterError(
            f"Longitude must be between -180 and 180, got {lon}"
        )

    return coordinates


def validate_bbox(bbox: object) -> tuple[float, float, float, float]:
    """Validate bounding box query parameter and raise error if invalid.

    Args:
        bbox: Value representing the bbox query parameter as (min_lon, min_lat, max_lon, max_lat).

    Returns:
        The unaltered validated bounding box tuple.

    Raises:
        InvalidParameterError: If bounding box is not a valid 4-value tuple with valid coordinate ranges.
    """
    if not isinstance(bbox, tuple):
        raise InvalidParameterError(
            f"Bounding box must be a tuple, got {type(bbox).__name__}"
        )

    if len(bbox) != 4:
        raise InvalidParameterError(
            f"Bounding box must have exactly 4 values, got {len(bbox)}"
        )

    if not all(isinstance(x, (int, float)) for x in bbox):
        raise InvalidParameterError("Bounding box must contain only numbers")

    min_lon, min_lat, max_lon, max_lat = bbox

    if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
        raise InvalidParameterError(
            f"Latitudes must be between -90 and 90, got {min_lat}, {max_lat}"
        )

    if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
        raise InvalidParameterError(
            f"Longitudes must be between -180 and 180, got {min_lon}, {max_lon}"
        )

    if min_lon >= max_lon:
        raise InvalidParameterError(
            f"minimum longitude value must be less than maximum longtitude, got {min_lon} >= {max_lon}"
        )

    if min_lat >= max_lat:
        raise InvalidParameterError(
            f"minimum latitude must be less than maximum latitude, got {min_lat} >= {max_lat}"
        )

    return bbox


def geospatial_params_exclusivity_check(
    coordinates: object | None, radius: object | None, bbox: object | None
) -> bool:
    """Check if geospatial query parameter combination is valid.

    Validates that:
    - coordinates and radius are either both provided or both absent
    - bbox is mutually exclusive with coordinates/radius

    Args:
        coordinates: Coordinates query parameter value.
        radius: Radius query parameter value.
        bbox: Bounding box query parameter value.

    Returns:
        True if parameters form a valid combination, False otherwise.
    """
    has_coordinates = coordinates is not None
    has_radius = radius is not None
    has_bbox = bbox is not None

    if has_coordinates != has_radius:
        return False

    if has_bbox and (has_coordinates or has_radius):
        return False

    return True


def validate_geospatial_params(
    coordinates: object | None, radius: object | None, bbox: object | None
) -> CoordinatesRadius | BboxOnly | tuple[None, None, None]:
    """Validate geospatial query parameters and raise error if invalid.

    Args:
        coordinates: Coordinates query parameter value.
        radius: Radius query parameter value.
        bbox: Bounding box query parameter value.

    Returns:
        Validated geospatial parameters as one of:
        - (coordinates, radius, None) if coordinates/radius provided
        - (None, None, bbox) if bbox provided
        - (None, None, None) if no geospatial parameters provided

    Raises:
        InvalidParameterError: If parameter combination is invalid or values fail validation.
    """
    if not geospatial_params_exclusivity_check(coordinates, radius, bbox):
        has_coordinates = coordinates is not None
        has_radius = radius is not None
        has_bbox = bbox is not None
        if has_coordinates and not has_radius:
            raise InvalidParameterError("coordinates requires radius parameter")

        if has_radius and not has_coordinates:
            raise InvalidParameterError("radius requires coordinates parameter")

        if has_bbox and (has_coordinates or has_radius):
            raise InvalidParameterError(
                "bbox cannot be used with coordinates/radius parameters"
            )
    if bbox is not None:
        validated_bbox = validate_bbox(bbox)
        return (None, None, validated_bbox)
    elif coordinates is not None and radius is not None:
        validated_coords = validate_coordinates(coordinates)
        validated_radius = validate_radius(radius)
        return (validated_coords, validated_radius, None)
    else:
        return (None, None, None)


def page_check(page: object) -> TypeGuard[int]:
    """Check if value is a valid page number.

    Args:
        page: Value to validate as a page query parameter.

    Returns:
        True if value is a positive integer, False otherwise.
    """
    if isinstance(page, bool):
        return False
    if not isinstance(page, int):
        return False
    return page > 0


def validate_page_param(page: object) -> int:
    """Validate page query parameter and raise error if invalid.

    Args:
        page: Value representing the page query parameter.

    Returns:
        The unaltered validated page integer.

    Raises:
        InvalidParameterError: If page is not a positive integer.
    """
    if not page_check(page):
        message = f"page query parameter must be an integer greater than zero, got {type(page)} - {page}"
        raise InvalidParameterError(message)
    return page


def limit_check(limit: int) -> TypeGuard[int]:
    """Check if value is a valid limit number.

    Args:
        limit: Value to validate as a limit query parameter.

    Returns:
        True if value is an integer between 1 and MAX_LIMIT (1,000), False otherwise.
    """
    if isinstance(limit, bool):
        return False
    if not isinstance(limit, int):
        return False
    return 0 < limit <= MAX_LIMIT


def validate_limit_param(limit: int) -> int:
    """Validate limit query parameter and raise error if invalid.

    Args:
        limit: Value representing the limit query parameter (results per page).

    Returns:
        The unaltered validated limit integer.

    Raises:
        InvalidParameterError: If limit is not an integer between 1 and 1,000.
    """
    if not limit_check(limit):
        message = f"limit query parameter must be an integer greater than zero and less than or equal to {MAX_LIMIT:,}, got {limit}"
        raise InvalidParameterError(message)
    return limit


def is_int_list(id: list[object]) -> TypeGuard[list[int]]:
    """Check if all items in list are valid integer IDs.

    Args:
        id: List of values to validate.

    Returns:
        True if all items are valid integer IDs, False otherwise.
    """
    return all(isinstance(x, int) and integer_id_check(x) for x in id)


def validate_integer_or_list_integer_params(
    param_name: str, id: list[object] | object
) -> list[int] | int:
    """Validate query parameter that accepts either a single integer or list of integers.

    Args:
        param_name: Name of the query parameter (for error messages).
        id: Value representing a query parameter that can be an integer or list of integers.

    Returns:
        The unaltered validated integer or list of integers.

    Raises:
        InvalidParameterError: If value is not a valid integer or list of valid integers.
    """
    if isinstance(id, int) and integer_id_check(id):
        return id
    if isinstance(id, list):
        if not is_int_list(id):
            message = f"query parameter {param_name} must be a valid list of integers, got list containing: {set(type(x).__name__ for x in id)}"
            raise InvalidParameterError(message)
        return id
    message = f"query parameter {param_name} must be an integer or list of integers, got: {type(id)}"
    raise InvalidParameterError(message)


_ISO_CODES_FROZEN = frozenset(ISO_CODES)


def iso_check(code: object) -> TypeGuard[str]:
    """Check if value is a valid ISO-3166-1 alpha-2 country code.

    Args:
        code: Value to validate as an ISO country code query parameter.

    Returns:
        True if value is a valid 2-letter ISO country code (case-insensitive), False otherwise.
    """
    if not isinstance(code, str):
        return False
    return len(code) == 2 and code.upper() in _ISO_CODES_FROZEN


def validate_iso_param(code: str) -> str:
    """Validate ISO country code query parameter and raise error if invalid.

    Args:
        code: Value representing the iso query parameter (ISO-3166-1 alpha-2 country code).

    Returns:
        The unaltered validated ISO country code string.

    Raises:
        InvalidParameterError: If code is not a valid ISO-3166-1 alpha-2 country code.
    """
    if not iso_check(code):
        message = (
            f"iso value must be a valid ISO-3166-1 alpha-2 country code, got {code}"
        )
        raise InvalidParameterError(message)
    return code


def validate_monitor(monitor: object) -> bool:
    """Validate monitor query parameter and raise error if invalid.

    Args:
        monitor: Value representing the monitor query parameter.

    Returns:
        The unaltered validated monitor boolean.

    Raises:
        InvalidParameterError: If monitor is not a boolean.
    """
    if not isinstance(monitor, bool):
        message = f"monitor parameter must be a boolean, got: {type(monitor)}"
        raise InvalidParameterError(message)
    return monitor


def validate_mobile(mobile: object) -> bool:
    """Validate mobile query parameter and raise error if invalid.

    Args:
        mobile: Value representing the mobile query parameter.

    Returns:
        The unaltered validated mobile boolean.

    Raises:
        InvalidParameterError: If mobile is not a boolean.
    """
    if not isinstance(mobile, bool):
        message = f"mobile parameter must be a boolean, got: {type(mobile)}"
        raise InvalidParameterError(message)
    return mobile


def validate_order_by(order_by: object) -> str:
    """Validate order_by query parameter and raise error if invalid.

    Args:
        order_by: Value representing the order_by query parameter (field name to sort by).

    Returns:
        The unaltered validated order_by string.

    Raises:
        InvalidParameterError: If order_by is not a string.
    """
    if not isinstance(order_by, str):
        message = f"mobile parameter must be a boolean, got: {type(order_by)}"
        raise InvalidParameterError(message)
    return order_by


def validate_sort_order(sort_order: object) -> SortOrder:
    """Validate sort_order query parameter and raise error if invalid.

    Args:
        sort_order: Value representing the sort_order query parameter.

    Returns:
        The unaltered validated sort_order value (one of: 'ASC', 'DESC', 'asc', 'desc').

    Raises:
        InvalidParameterError: If sort_order is not a valid sort order string.
    """
    if not isinstance(sort_order, str):
        message = f"sort_order parameter must be a string, got: {type(sort_order)}"
        raise InvalidParameterError(message)

    if sort_order not in _SORT_ORDER_VALUES:
        raise InvalidParameterError(f"Invalid sort_order: {sort_order}")

    return cast(SortOrder, sort_order)


def data_check(data: object) -> TypeGuard[Data]:
    """Check if value is a valid data type.

    Args:
        data: Value to validate as a data path parameter.

    Returns:
        True if value is one of: 'measurements', 'hours', 'days', 'years', False otherwise.
    """
    if not isinstance(data, str):
        return False
    return data in _DATA_VALUES


def validate_data(data: object) -> Data:
    """Validate data path parameter and raise error if invalid.

    Args:
        data: Value representing the data path parameter.

    Returns:
        The unaltered validated data value.

    Raises:
        InvalidParameterError: If data is not one of the valid data types.
    """
    if not data_check(data):
        raise InvalidParameterError(
            f"Invalid data type: {data}. Must be one of: {', '.join(_DATA_VALUES)}"
        )
    return data


def rollup_check(rollup: object) -> TypeGuard[Rollup]:
    """Check if value is a valid rollup type.

    Args:
        rollup: Value to validate as a rollup path parameter.

    Returns:
        True if value is a valid rollup type (e.g., 'hourly', 'daily', 'monthly'), False otherwise.
    """
    if not isinstance(rollup, str):
        return False
    return rollup in _ROLLUP_VALUES


def validate_rollup(rollup: object) -> Rollup:
    """Validate rollup path parameter and raise error if invalid.

    Args:
        rollup: Value representing the rollup path parameter.

    Returns:
        The unaltered validated rollup value.

    Raises:
        InvalidParameterError: If rollup is not one of the valid rollup types.
    """
    if not rollup_check(rollup):
        raise InvalidParameterError(
            f"Invalid rollup type: {rollup}. Must be one of: {', '.join(_ROLLUP_VALUES)}"
        )
    return rollup


def iso8601_check(value: object) -> TypeGuard[str]:
    """Check if value is a valid ISO-8601 datetime string.

    Args:
        value: Value to validate as an ISO-8601 datetime string.

    Returns:
        True if value is a valid ISO-8601 formatted datetime string, False otherwise.
    """
    if not isinstance(value, str):
        return False

    try:
        # Replace 'Z' with '+00:00' for Python 3.10
        # https://docs.python.org/3/whatsnew/3.11.html#datetime
        datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False


def datetime_check(value: object) -> TypeGuard[datetime.datetime | str]:
    """Check if value is a valid datetime object or ISO-8601 string.

    Args:
        value: Value to validate as a datetime query parameter.

    Returns:
        True if value is a datetime object or valid ISO-8601 string, False otherwise.
    """
    is_datetime = isinstance(value, datetime.datetime)
    is_str = isinstance(value, str)
    if not any([is_datetime, is_str]):
        return False
    if is_str:
        return iso8601_check(value)
    return True


def to_datetime(value: datetime.datetime | str) -> datetime.datetime:
    """Convert value to datetime object if not already a datetime.

    Args:
        value: Datetime object or ISO-8601 datetime string.

    Returns:
        Datetime object (converted from string if necessary).
    """
    if isinstance(value, datetime.datetime):
        return value
    return datetime.datetime.fromisoformat(value)


def validate_datetime_params(
    datetime_from: object, datetime_to: object
) -> tuple[datetime.datetime, datetime.datetime | None]:
    """Validate datetime query parameters and raise error if invalid.

    Args:
        datetime_from: Value representing the datetime_from query parameter (start date/time).
        datetime_to: Value representing the datetime_to query parameter (end date/time), or None.

    Returns:
        Tuple of validated datetime objects (datetime_from, datetime_to), where datetime_to may be None.

    Raises:
        Exception: If either datetime value is invalid.
    """
    if datetime_to:
        if not datetime_check(datetime_from) or not datetime_check(datetime_to):
            raise Exception()
        return (to_datetime(datetime_from), to_datetime(datetime_to))
    else:
        if not datetime_check(datetime_from):
            raise Exception()
        return (to_datetime(datetime_from), None)


def parameter_type_check(parameter_type: object) -> TypeGuard[ParameterType]:
    """Check if value is a valid parameter type.

    Args:
        parameter_type: Value to validate as a parameter_type query parameter.

    Returns:
        True if value is one of: 'pollutant', 'meteorological', False otherwise.
    """
    if not isinstance(parameter_type, str):
        return False
    return parameter_type in _PARAMETER_TYPE_VALUES


def validate_parameter_type(parameter_type: object) -> ParameterType:
    """Validate parameter_type query parameter and raise error if invalid.

    Args:
        parameter_type: Value representing the parameter_type query parameter.

    Returns:
        The unaltered validated parameter_type value.

    Raises:
        InvalidParameterError: If parameter_type is not one of the valid parameter_type types.
    """
    if not parameter_type_check(parameter_type):
        raise InvalidParameterError(
            f"Invalid parameter_type type: {parameter_type}. Must be one of: {', '.join(_PARAMETER_TYPE_VALUES)}"
        )
    return parameter_type
