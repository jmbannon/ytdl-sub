import pytest

from ytdl_subscribe.validators.base.validators import BoolValidator
from ytdl_subscribe.validators.exceptions import ValidationException


@pytest.mark.parametrize("value", [True, False])
def test_bool_validator(value):
    bool_validator = BoolValidator(name="good_bool_validator", value=value)
    assert bool_validator._name == "good_bool_validator"
    assert bool_validator._value == value
    assert bool_validator.value == value


@pytest.mark.parametrize("value", [None, {}, "True", 0])
def test_bool_validator_fails_bad_value(value):
    with pytest.raises(
        ValidationException, match="Validation error in fail: should be of type bool"
    ):
        _ = BoolValidator(name="fail", value=value)
