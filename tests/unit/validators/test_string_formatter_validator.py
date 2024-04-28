import pytest
from yt_dlp.utils import sanitize_filename

from ytdl_sub.utils.exceptions import StringFormattingException
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesDictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import UnstructuredDictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import (
    UnstructuredOverridesDictFormatterValidator,
)


@pytest.mark.parametrize(
    "string_formatter_class", [StringFormatterValidator, OverridesStringFormatterValidator]
)
class TestStringFormatterValidator(object):
    def test_parse(self, string_formatter_class):
        format_string = "Here is my {var_one1} and {var_two} 💩"
        validator = string_formatter_class(name="test_format_variables", value=format_string)

        assert validator.format_string == format_string

    @pytest.mark.parametrize(
        "format_string",
        [
            "Try {var_one{ and {var_two}",
            "Single open {",
            "Single close }",
            "Try }var_one} and {var_one}",
        ],
    )
    def test_validate_fail_uneven_brackets(self, string_formatter_class, format_string):
        with pytest.raises(ValidationException, match="Validation error in fail:"):
            _ = string_formatter_class(name="fail", value=format_string)

    @pytest.mark.parametrize(
        "format_string",
        [
            "Try {1starting_number}",
            "Try {_underscore_first}",
            "Try {VAR1} caps w/numbers",
            "Try {internal{bracket}}",
            "Try }backwards{ facing",
            "Try {var_1}}{",
            "Try {} empty",
        ],
    )
    def test_validate_fail_bad_variable(self, string_formatter_class, format_string):
        with pytest.raises(ValidationException, match="Validation error in fail:"):
            _ = string_formatter_class(name="fail", value=format_string)


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

        assert validator.dict_with_format_strings == {
            "key1": key1_format_string,
            "key2": key2_format_string,
        }


class TestUnstructuredDictFormatterValidator(object):
    @pytest.mark.parametrize(
        "dict_validator_class, expected_formatter_class",
        [
            (UnstructuredDictFormatterValidator, StringFormatterValidator),
            (UnstructuredOverridesDictFormatterValidator, OverridesStringFormatterValidator),
        ],
    )
    def test_validates_values(self, dict_validator_class, expected_formatter_class):
        key1_format_string = "string with {variable}"
        key2_format_string = "no variables"
        key3_int = 3
        key4_float = 4.132
        key5_bool = True
        key6_map = {"{variable}_key": "value", "static_key": "{variable}_value"}
        key7_list = ["list_1", "list_{variable_2}"]
        key8_many_vars = "string {variable1} with multiple {variable2}"
        validator = dict_validator_class(
            name="validator",
            value={
                "key1": key1_format_string,
                "key2": key2_format_string,
                "key3": key3_int,
                "key4": key4_float,
                "key5": key5_bool,
                "key6": key6_map,
                "key7": key7_list,
                "key8": key8_many_vars,
            },
        )

        assert len(validator.dict) == 8
        assert all(isinstance(val, expected_formatter_class) for val in validator.dict.values())
        assert validator.dict_with_format_strings == {
            "key1": "{ %concat( %string( '''string with ''' ), %string( variable ) ) }",
            "key2": "no variables",
            "key3": "{ %int(3) }",
            "key4": "{ %float(4.132) }",
            "key5": "{ %int(True) }",
            "key6": "{ { %concat( %string( variable ), %string( '''_key''' ) ): '''value''', '''static_key''': %concat( %string( variable ), %string( '''_value''' ) ) } }",
            "key7": "{ [ '''list_1''', %concat( %string( '''list_''' ), %string( variable_2 ) ) ] }",
            "key8": "{ %concat( %string( '''string ''' ), %string( variable1 ), %string( ''' with multiple ''' ), %string( variable2 ) ) }",
        }
