import pytest

from ytdl_subscribe.validators.base.validators import StringValidator
from ytdl_subscribe.validators.exceptions import ValidationException


@pytest.mark.parametrize("value", ["a", "unicode 💩", ""])
def test_string_validator(value):
    bool_validator = StringValidator(name="good_str_validator", value=value)
    assert bool_validator._name == "good_str_validator"
    assert bool_validator._value == value
    assert bool_validator.value == value


@pytest.mark.parametrize("value", [None, {}, True, 0])
def test_bool_validator_fails_bad_value(value):
    with pytest.raises(
        ValidationException, match="Validation error in fail: should be of type string"
    ):
        _ = StringValidator(name="fail", value=value)
