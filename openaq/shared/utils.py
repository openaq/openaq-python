"""Various shared utilities."""

from openaq.shared.exceptions import BadRequestError, IdentifierOutOfBoundsError


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
        BadRequestError: Raised for HTTP 400 error, indicating a client request error.

    """
    if not integer_id_check(id):
        message = f"ID values must be between 1 and {1 << 31 - 1}, got {id}"
        raise IdentifierOutOfBoundsError(message)
    return id
