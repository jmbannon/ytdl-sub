import pytest
from unit.script.conftest import single_variable_output

from ytdl_sub.script.script import Script


class TestNumericFunctions:
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
