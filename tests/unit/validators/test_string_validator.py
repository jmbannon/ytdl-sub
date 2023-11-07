import pytest

from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.validators.validators import StringValidator


@pytest.mark.parametrize("value", ["a", "unicode 💩", "", 1, 3.14, True, False])
def test_string_validator(value):
    string_validator = StringValidator(name="good_str_validator", value=value)
    assert string_validator._name == "good_str_validator"
    assert string_validator._value == str(value)
    assert string_validator.value == str(value)


@pytest.mark.parametrize("value", [None, {}, True, 0])
def test_bool_validator_fails_bad_value(value):
    with pytest.raises(
        ValidationException, match="Validation error in fail: should be of type string"
    ):
        _ = StringValidator(name="fail", value=value)
