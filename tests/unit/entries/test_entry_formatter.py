import pytest

from ytdl_subscribe.validators.base.string_formatter_validator import (
    StringFormatterValidator,
)
from ytdl_subscribe.validators.exceptions import ValidationException


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


class TestEntryFormatter(object):
    def test_parse(self):
        format_string = "Here is my {var_one} and {var_two} 💩"
        assert StringFormatterValidator(
            name="test_format_variables", value=format_string
        ).format_variables == ["var_one", "var_two"]

    def test_parse_no_variables(self):
        format_string = "No vars 💩"
        assert (
            StringFormatterValidator(
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
    def test_parse_fail_uneven_brackets(
        self, format_string, error_message_unequal_brackets_str
    ):
        expected_error_msg = (
            f"Validation error in fail: {error_message_unequal_brackets_str}"
        )

        with pytest.raises(ValidationException, match=expected_error_msg):
            _ = StringFormatterValidator(name="fail", value=format_string)

    @pytest.mark.parametrize(
        "format_string",
        [
            "Try {var1} no numbers",
            "Try {VAR1} no caps",
            "Try {internal{bracket}}",
            "Try }backwards{ facing",
            "Try {var_1}}{",
            "Try {} empty",
        ],
    )
    def test_parse_fail_variable(
        self, format_string, error_message_unequal_regex_matches_str
    ):
        expected_error_msg = (
            f"Validation error in fail: {error_message_unequal_regex_matches_str}"
        )

        with pytest.raises(ValidationException, match=expected_error_msg):
            _ = StringFormatterValidator(name="fail", value=format_string)
