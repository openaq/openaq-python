from openaq.shared.exceptions import IdentifierOutOfBoundsError
import pytest


from openaq.shared.utils import integer_id_check, validate_integer_id


@pytest.mark.parametrize(
    "id,valid",
    [
        (-1, False),
        (0, False),
        (1, True),
        (2_147_483_647 - 1, True),
        (2_147_483_647, True),
        (2_147_483_647 + 1, False),
        (999_999_999_999, False),
    ],
)
def test_integer_id_check(id: int, valid: bool):
    assert integer_id_check(id) == valid


@pytest.mark.parametrize(
    "id",
    [
        (-1),
        (0),
        (2_147_483_647 + 1),
        (999_999_999_999),
    ],
)
def test_validate_integer_id_throws(id: int):
    with pytest.raises(IdentifierOutOfBoundsError):
        validate_integer_id(id)
