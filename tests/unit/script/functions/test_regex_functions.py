import pytest
from unit.script.conftest import single_variable_output

from ytdl_sub.script.utils.exceptions import FunctionRuntimeException


class TestRegexFunctions:
    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("'ow', 'lower'", []),
            ("'.*ow.*', 'lower'", ["lower"]),
            ("'.*(ow).*', 'lower'", ["lower", "ow"]),
            ("'(.*)(ow)(.*)', 'lower'", ["lower", "l", "ow", "er"]),
        ],
    )
    def test_regex_match(self, values: str, expected_output: str):
        output = single_variable_output(f"{{%regex_match({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("'ow', 'lower'", ["lower"]),
            ("'.*ow.*', 'lower'", ["lower"]),
            ("'.*(ow).*', 'lower'", ["lower", "ow"]),
            ("'(.*)(ow)(.*)', 'lower'", ["lower", "l", "ow", "er"]),
        ],
    )
    def test_regex_search(self, values: str, expected_output: str):
        output = single_variable_output(f"{{%regex_search({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("'ow', 'lower'", []),
            ("'.*ow.*', 'lower'", ["lower"]),
            ("'.*(ow).*', 'lower'", ["lower", "ow"]),
            ("'(.*)(ow)(.*)', 'lower'", ["lower", "l", "ow", "er"]),
        ],
    )
    def test_regex_fullmatch(self, values: str, expected_output: str):
        output = single_variable_output(f"{{%regex_fullmatch({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("'[^A-Za-z0-9 ]', '', 'This title is AWESOME!!'", "This title is AWESOME"),
            ("'\s+', '_', 'Consolidate   spaces'", "Consolidate_spaces"),
            (
                "'(words) are (reordered)', '\\2 are \\1', 'Oh words are reordered'",
                "Oh reordered are words",
            ),
            ("'MATCH', '', 'matcha is great'", "matcha is great"),
        ],
    )
    def test_regex_sub(self, values: str, expected_output: str):
        output = single_variable_output(f"{{%regex_sub({values})}}")
        assert output == expected_output

    def test_regex_capture_many_fails_no_match(self):
        with pytest.raises(
            FunctionRuntimeException,
            match="no regex strings were captured for input string the string",
        ):
            single_variable_output(
                f"""{{
            %regex_capture_many(
                "the string",
                [
                    "no (.*) match",
                    "not here either (.*)"
                ]
            )
        }}"""
            )

    def test_regex_capture_many_fails_unequal_capture_groups(self):
        with pytest.raises(
            FunctionRuntimeException,
            match="regex_array elements must contain the same number of capture groups",
        ):
            single_variable_output(
                f"""{{
            %regex_capture_many(
                "the string",
                [
                    "no (.*) match",
                    "(.*) not equal to 1 (.*)"
                ]
            )
        }}"""
            )
