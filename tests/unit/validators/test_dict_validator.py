import pytest

from ytdl_subscribe.validators.base.validators import BoolValidator
from ytdl_subscribe.validators.base.validators import DictValidator
from ytdl_subscribe.validators.base.validators import StringValidator
from ytdl_subscribe.validators.exceptions import ValidationException


@pytest.mark.parametrize(
    "value", [{}, {"key": "value"}, {"b": {}, "a": "keys_out_of_order"}]
)
def test_dict_validator(value):
    dict_validator = DictValidator(name="good_dict_validator", value=value)
    assert dict_validator._name == "good_dict_validator"
    assert dict_validator._value == value
    assert dict_validator._dict == value
    assert dict_validator._keys == sorted(list(value.keys()))


@pytest.mark.parametrize("value", [None, "a", {"set"}, 0])
def test_dict_validator_fails_bad_value(value):
    with pytest.raises(
        ValidationException, match="Validation error in fail: should be of type object"
    ):
        _ = DictValidator(name="fail", value=value)


@pytest.mark.parametrize(
    "value, validator_class", [("string", StringValidator), (False, BoolValidator)]
)
def test_dict_validator_validate_key(value, validator_class):
    dict_validator = DictValidator(name="validate_key", value={"key_name": value})
    validated_key = dict_validator._validate_key(
        key="key_name", validator=validator_class
    )

    assert isinstance(validated_key, validator_class)
    assert validated_key.value == value


def test_dict_validator_validate_key_errors_missing():
    dict_validator = DictValidator(name="validate_key", value={"key": None})
    with pytest.raises(
        ValidationException,
        match="Validation error in validate_key: key_name is missing when it should be present.",
    ):
        _ = dict_validator._validate_key(key="key_name", validator=StringValidator)


@pytest.mark.parametrize("bad_value", [True, None, {}])
def test_dict_validator_validate_key_errors_bad_validation(bad_value):
    dict_validator = DictValidator(name="parent", value={"child": bad_value})
    with pytest.raises(
        ValidationException,
        match="Validation error in parent.child: should be of type string",
    ):
        _ = dict_validator._validate_key(key="child", validator=StringValidator)


@pytest.mark.parametrize(
    "value, validator_class", [("string", StringValidator), (False, BoolValidator)]
)
def test_dict_validator_validate_key_if_present(value, validator_class):
    dict_validator = DictValidator(name="validate_key", value={"key_name": value})
    validated_key = dict_validator._validate_key_if_present(
        key="key_name", validator=validator_class
    )

    assert isinstance(validated_key, validator_class)
    assert validated_key.value == value


def test_dict_validator_validate_key_if_present_is_missing():
    dict_validator = DictValidator(name="validate_key", value={"key_name": None})
    out = dict_validator._validate_key_if_present(
        key="non_existent_key", validator=StringValidator
    )

    assert out is None


def test_dict_validator_validate_key_if_present_is_missing_with_default():
    dict_validator = DictValidator(name="validate_key", value={"key_name": None})
    out = dict_validator._validate_key_if_present(
        key="non_existent_key", validator=StringValidator, default="default"
    )

    assert isinstance(out, StringValidator)
    assert out.value == "default"


@pytest.mark.parametrize("bad_value", [True, None, {}])
def test_dict_validator_validate_key_errors_none_bad_validation(bad_value):
    dict_validator = DictValidator(name="parent", value={"child": bad_value})
    with pytest.raises(
        ValidationException,
        match="Validation error in parent.child: should be of type string",
    ):
        _ = dict_validator._validate_key(key="child", validator=StringValidator)
