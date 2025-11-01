"""Various shared utilities."""

from typing import Any, Mapping
from openaq.shared.constants import ISO_CODES, MAX_LIMIT, MAX_RADIUS
from openaq.shared.exceptions import (
    IdentifierOutOfBoundsError,
    InvalidQueryParameterError,
)


def integer_id_check(id: int) -> bool:
    """Checks that the given id is with 32 bit integer range and is positive.

    Args:
        id: integer representing an id field in the OpenAQ API.

    Returns:
        Boolean
    """
    return id > 0 and id < 1 << 31


def validate_integer_id(id: int) -> int:
    """Validate ID and raise error if invalid.

    Args:
        id: integer representing an id field in the OpenAQ API.

    Raises:
        IdentifierOutOfBoundsError: Exception indicating the input id parameter
        is outside the valid bounds.

    """
    if not integer_id_check(id):
        message = f"ID values must be between 1 and {1 << 31 - 1}, got {id}"
        raise IdentifierOutOfBoundsError(message)
    return id


def validate_geospatial_params(params: Mapping[str, Any]) -> Mapping[str, Any]:
    """Validates geospatial ('bbox', 'coordinates', 'radius') query parameters.

    Args:
        params: A dictionary of values

    Returns:
        Mapping: the unaltered input dictionary if all validation checks pass.

    Raises:
        InvalidQueryParameterError:
    """
    has_radius = 'radius' in params
    has_coordinates = 'coordinates' in params
    has_bbox = 'bbox' in params

    if not (has_radius or has_coordinates or has_bbox):
        return params

    if has_bbox and (has_radius or has_coordinates):
        raise InvalidQueryParameterError(
            "'bbox' cannot be used with 'radius' and/or 'coordinates'"
        )

    if has_bbox:
        return params

    if has_radius != has_coordinates:
        missing = 'coordinates' if has_radius else 'radius'
        raise InvalidQueryParameterError(
            f"'{missing}' is required when using radius/coordinates"
        )

    if has_radius:
        radius = params['radius']
        if not (0 < radius <= MAX_RADIUS):
            raise InvalidQueryParameterError(
                f"radius must be greater than zero and less than or equal to "
                f"{MAX_RADIUS:,}, got {radius}"
            )

    return params


def check_limit_within_bounds(limit: int) -> bool:
    """Checks if limit value is with bounds [0,1_000].

    Args:
        limit: integer value for setting the number of results per page.

    Returns:
        bool: True if limit is valid, False otherwise.
    """
    return 0 < limit <= MAX_LIMIT


def validate_limit_param(limit: int) -> int:
    """Validates 'limit' query parameter and raise error if invalid.

    Args:
        limit: integer value for setting the number of results per page.

    Returns:
        int: unaltered input value if check passes.

    Raises:
        InvalidQueryParameterError:
    """
    if not check_limit_within_bounds(limit):
        message = f"limit query parameter must be greater than zero and less than or equal to {MAX_LIMIT:,}, got {limit}"
        raise InvalidQueryParameterError(message)
    return limit


def validate_params(params: Mapping[str, Any]) -> Mapping[str, Any]:
    if 'limit' in params:
        params = validate_limit_param(params)
    has_radius = 'radius' in params
    has_coordinates = 'coordinates' in params
    has_bbox = 'bbox' in params
    if has_radius | has_coordinates | has_bbox:
        params = validate_geospatial_params(params)
    if 'iso' in params:
        params = validate_iso_param(params)
    return params


_ISO_CODES_FROZEN = frozenset(ISO_CODES)


def iso_check(code: str) -> bool:
    """Checks if iso is valid ISO-3166-1 alpha-2 value.

    Args:
        code: string representing ISO-3166-1 alpha-2 country code

    Returns:
        bool: True if code is valid, False otherwise.
    """
    return len(code) == 2 and code.upper() in _ISO_CODES_FROZEN


def validate_iso_param(code: str) -> str:
    """Validate 'iso' query parameter and raise error if invalid.

    Args:
        code: string representing ISO-3166-1 alpha-2 country code.

    Returns:
        str: unaltered input value if check passes.

    Raises:
        InvalidQueryParameterError:

    """
    if not iso_check(code):
        message = (
            f"iso value must be a valid ISO-3166-1 alpha-2 country code, got {code}"
        )
        raise InvalidQueryParameterError(message)
    return code
