import pytest
from unit.script.conftest import single_variable_output

from ytdl_sub.script.script import Script


class TestNumericFunctions:
    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("'lower'", "LOWER"),
            ("'UPPER'", "UPPER"),
        ],
    )
    def test_upper(self, values: str, expected_output: str):
        output = single_variable_output(f"{{%upper({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("'lower'", "lower"),
            ("'UPPER'", "upper"),
        ],
    )
    def test_lower(self, values: str, expected_output: str):
        output = single_variable_output(f"{{%lower({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("'lower First word'", "Lower first word"),
            ("'UPPER First word'", "Upper first word"),
        ],
    )
    def test_capitalize(self, values: str, expected_output: str):
        output = single_variable_output(f"{{%capitalize({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("'lower First word'", "Lower First Word"),
            ("'UPPER First word'", "Upper First Word"),
        ],
    )
    def test_titlecase(self, values: str, expected_output: str):
        output = single_variable_output(f"{{%titlecase({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            (
                "'lower First word second word', 'word', 'string'",
                "lower First string second string",
            ),
            (
                "'lower First word second word', 'word', 'string', 1",
                "lower First string second word",
            ),
        ],
    )
    def test_replace(self, values: str, expected_output: str):
        output = single_variable_output(f"{{%replace({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("'lower First word'", "lower First word"),
            ("'lower First word', ' second', ' string'", "lower First word second string"),
        ],
    )
    def test_concat(self, values: str, expected_output: str):
        output = single_variable_output(f"{{%concat({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("'HI', 6, '.'", "....HI"),
            ("'HI', 2, '.'", "HI"),
        ],
    )
    def test_pad(self, values: str, expected_output: str):
        output = single_variable_output(f"{{%pad({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("2012, 6", "002012"),
            ("2012, 2", "2012"),
        ],
    )
    def test_pad_zero(self, values: str, expected_output: str):
        output = single_variable_output(f"{{%pad_zero({values})}}")
        assert output == expected_output
