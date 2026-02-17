import pytest
from unit.script.conftest import single_variable_output


class TestNumericFunctions:
    @pytest.mark.parametrize(
        "values, expected_output", [("1, 2, 3", 6), ("1", 1), ("-1, -2, -3", -6), ("1.1, 1.2", 2.3)]
    )
    def test_add(self, values: str, expected_output: int):
        output = single_variable_output(f"{{%add({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output", [("1, 2, 3", -4), ("1", 1), ("-1, -2, -3", 4), ("1.5, 2.5", -1)]
    )
    def test_sub(self, values: str, expected_output: int):
        output = single_variable_output(f"{{%sub({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [("1, 2, 3", 6), ("1", 1), ("-1, -2, -3", -6), ("1.5, 2.5", 3.75)],
    )
    def test_mul(self, values: str, expected_output: int):
        output = single_variable_output(f"{{%mul({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output", [("2, 2", 1), ("10, 5", 2), ("4.5, 0.5", 9), ("-3.5, -2", 1.75)]
    )
    def test_div(self, values: str, expected_output: int):
        output = single_variable_output(f"{{%div({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("8, 3", 2),
            ("1, 1", 0),
        ],
    )
    def test_mod(self, values: str, expected_output: int):
        output = single_variable_output(f"{{%mod({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("8, 3, 0.3, 0.2, 1.4, 99.9", 99.9),
            ("1, 1, 0, 1", 1),
        ],
    )
    def test_max(self, values: str, expected_output: int):
        output = single_variable_output(f"{{%max({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("8, 3, 0.3, 0.2, 1.4, 99.9", 0.2),
            ("1, 1, 0, 1", 0),
        ],
    )
    def test_min(self, values: str, expected_output: int):
        output = single_variable_output(f"{{%min({values})}}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("2, 2", 2**2),
            ("9, 0.5", 9**0.5),
            ("4.4, 2.2", 4.4**2.2),
        ],
    )
    def test_pow(self, values: str, expected_output: float):
        output = single_variable_output(f"{{ %pow({values}) }}")
        assert output == expected_output

    @pytest.mark.parametrize(
        "values, expected_output",
        [
            ("5", [0, 1, 2, 3, 4]),
            ("5, 1", [1, 2, 3, 4]),
            ("5, 1, 2", [1, 3]),
        ],
    )
    def test_range(self, values: str, expected_output: float):
        output = single_variable_output(f"{{ %range({values}) }}")
        assert output == expected_output
