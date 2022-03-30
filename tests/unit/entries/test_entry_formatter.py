import pytest

from ytdl_subscribe.entries.entry import EntryFormatter


@pytest.fixture
def error_message_unequal_brackets_str():
    return "Brackets are reserved for {variable_names} and should contain a single open and close bracket."


@pytest.fixture
def error_message_unequal_regex_matches_str():
    return "{variable_names} should only contain lowercase letters and underscores with a single open and close bracket."


@pytest.fixture
def error_message_prefix_generator():
    def _error_message_prefix_generator(format_string):
        return f"Format string '{format_string}' is invalid: "

    return _error_message_prefix_generator


@pytest.fixture
def error_message_unequal_brackets_generator(
    error_message_prefix_generator, error_message_unequal_brackets_str
):
    def _error_message_unequal_brackets_generator(format_string):
        return f"{error_message_prefix_generator(format_string)}{error_message_unequal_brackets_str}"

    return _error_message_unequal_brackets_generator


@pytest.fixture
def error_message_unequal_regex_matches_generator(
    error_message_prefix_generator, error_message_unequal_regex_matches_str
):
    def _error_message_unequal_regex_matches_generator(format_string):
        return f"{error_message_prefix_generator(format_string)}{error_message_unequal_regex_matches_str}"

    return _error_message_unequal_regex_matches_generator


class TestEntryFormatter(object):
    def test_parse(self):
        format_string = "Here is my {var_one} and {var_two} 💩"
        assert EntryFormatter(format_string).parse() == ["var_one", "var_two"]

    def test_parse_no_variables(self):
        format_string = "No vars 💩"
        assert EntryFormatter(format_string).parse() == []

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
        self, format_string, error_message_unequal_brackets_generator
    ):
        expected_error_msg = error_message_unequal_brackets_generator(format_string)

        with pytest.raises(ValueError, match=expected_error_msg):
            assert EntryFormatter(format_string).parse()

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
        self, format_string, error_message_unequal_regex_matches_generator
    ):
        expected_error_msg = error_message_unequal_regex_matches_generator(
            format_string
        )

        with pytest.raises(ValueError, match=expected_error_msg):
            assert EntryFormatter(format_string).parse()
