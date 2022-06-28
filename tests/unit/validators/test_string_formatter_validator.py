import pytest

from ytdl_sub.utils.exceptions import StringFormattingException
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesDictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator


@pytest.fixture
def error_message_unequal_brackets_str():
    return (
        "Brackets are reserved for {variable_names} and "
        "should contain a single open and close bracket."
    )


@pytest.fixture
def error_message_unequal_regex_matches_str():
    return (
        "{variable_names} should only contain lowercase letters and "
        "underscores with a single open and close bracket."
    )


@pytest.mark.parametrize(
    "string_formatter_class", [StringFormatterValidator, OverridesStringFormatterValidator]
)
class TestStringFormatterValidator(object):
    def test_parse(self, string_formatter_class):
        format_string = "Here is my {var_one} and {var_two} 💩"
        validator = string_formatter_class(name="test_format_variables", value=format_string)

        assert validator.format_string == format_string
        assert validator.format_variables == ["var_one", "var_two"]

    def test_format_variables(self, string_formatter_class):
        format_string = "No vars 💩"
        assert (
            string_formatter_class(
                name="test_format_variables_empty", value=format_string
            ).format_variables
            == []
        )

    @pytest.mark.parametrize(
        "format_string",
        [
            "Try {var_one{ and {var_two}",
            "Single open {",
            "Single close }",
            "Try }var_one} and {var_one}",
        ],
    )
    def test_validate_fail_uneven_brackets(
        self, string_formatter_class, format_string, error_message_unequal_brackets_str
    ):
        expected_error_msg = f"Validation error in fail: {error_message_unequal_brackets_str}"

        with pytest.raises(ValidationException, match=expected_error_msg):
            _ = string_formatter_class(name="fail", value=format_string)

    @pytest.mark.parametrize(
        "format_string",
        [
            "Try {var1} numbers",
            "Try {VAR1} caps w/numbers",
            "Try {internal{bracket}}",
            "Try }backwards{ facing",
            "Try {var_1}}{",
            "Try {} empty",
        ],
    )
    def test_validate_fail_bad_variable(
        self, string_formatter_class, format_string, error_message_unequal_regex_matches_str
    ):
        expected_error_msg = f"Validation error in fail: {error_message_unequal_regex_matches_str}"

        with pytest.raises(ValidationException, match=expected_error_msg):
            _ = string_formatter_class(name="fail", value=format_string)

    @pytest.mark.parametrize(
        "format_string, bad_variable",
        [
            ("keyword {while}", "while"),
            ("{try} {valid_var}", "try"),
        ],
    )
    def test_validate_fail_variable_keyword_or_not_identifier(
        self, string_formatter_class, format_string, bad_variable
    ):
        expected_error_msg = (
            f"Validation error in fail: "
            f"'{bad_variable}' is a Python keyword and cannot be used as a variable."
        )

        with pytest.raises(ValidationException, match=expected_error_msg):
            _ = string_formatter_class(name="fail", value=format_string)

    def test_entry_formatter_fails_missing_field(self, string_formatter_class):
        format_string = string_formatter_class(name="test", value=f"prefix {{bah_humbug}} suffix")
        variable_dict = {"varb": "a", "vara": "b"}
        expected_error_msg = (
            f"Validation error in test: Format variable 'bah_humbug' does not exist. "
            f"Available variables: {', '.join(sorted(variable_dict.keys()))}"
        )
        if string_formatter_class == OverridesStringFormatterValidator:
            expected_error_msg = (
                f"Validation error in test: Override variable 'bah_humbug' does not exist. "
                f"Available override variables: {', '.join(sorted(variable_dict.keys()))}"
            )

        with pytest.raises(StringFormattingException, match=expected_error_msg):
            assert format_string.apply_formatter(variable_dict=variable_dict)

    def test_string_formatter_single_field(self, string_formatter_class):
        uid = "this uid"
        format_string = string_formatter_class(name="test", value=f"prefix {{uid}} suffix")
        expected_string = f"prefix {uid} suffix"

        assert format_string.apply_formatter(variable_dict={"uid": uid}) == expected_string

    def test_entry_formatter_duplicate_fields(self, string_formatter_class):
        upload_year = "2022"
        format_string = string_formatter_class(
            name="test", value=f"prefix {{upload_year}} {{upload_year}} suffix"
        )
        expected_string = f"prefix {upload_year} {upload_year} suffix"

        assert (
            format_string.apply_formatter(variable_dict={"upload_year": upload_year})
            == expected_string
        )

    def test_entry_formatter_override_recursive(self, string_formatter_class):
        variable_dict = {
            "level_a": "level a",
            "level_b": "level b and {level_a}",
            "level_c": "level c and {level_b}",
        }

        format_string = string_formatter_class(name="test", value="level d and {level_c}")
        expected_string = "level d and level c and level b and level a"

        assert format_string.apply_formatter(variable_dict=variable_dict) == expected_string

    def test_entry_formatter_override_recursive_fail_cycle(self, string_formatter_class):
        variable_dict = {
            "level_a": "{level_b}",
            "level_b": "{level_a}",
        }

        # Max depth is 3 so should go level_a -(0)-> level_b -(1)-> level_a -(2)-> level_b
        expected_error_msg = (
            "Validation error in test: Attempted to format but failed after reaching max recursion "
            "depth of 3. Try to keep variables dependent on only one other variable at max. "
            "Unresolved variables: level_b"
        )

        format_string = string_formatter_class(name="test", value="{level_a}")

        with pytest.raises(StringFormattingException, match=expected_error_msg):
            _ = format_string.apply_formatter(variable_dict=variable_dict)


class TestDictFormatterValidator(object):
    @pytest.mark.parametrize(
        "dict_validator_class, expected_formatter_class",
        [
            (DictFormatterValidator, StringFormatterValidator),
            (OverridesDictFormatterValidator, OverridesStringFormatterValidator),
        ],
    )
    def test_validates_values(self, dict_validator_class, expected_formatter_class):
        key1_format_string = "string with {variable}"
        key2_format_string = "no variables"
        validator = dict_validator_class(
            name="validator",
            value={"key1": key1_format_string, "key2": key2_format_string},
        )

        assert isinstance(validator.dict["key1"], expected_formatter_class)
        assert isinstance(validator.dict["key2"], expected_formatter_class)

        assert validator.dict["key1"].format_string == key1_format_string
        assert validator.dict["key2"].format_string == key2_format_string

        assert validator.dict["key1"].format_variables == ["variable"]
        assert validator.dict["key2"].format_variables == []

        assert validator.dict_with_format_strings == {
            "key1": key1_format_string,
            "key2": key2_format_string,
        }
