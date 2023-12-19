import pytest
from unit.script.conftest import single_variable_output

from ytdl_sub.script.script import Script


class TestNumericFunctions:
    @pytest.mark.parametrize(
        "timestamp, date_format, expected_output",
        [
            (1596877200, "'%Y%m%d'", "20200808"),
            (1596877200, "'%m'", "08"),
        ],
    )
    def test_datetime_strftime(self, timestamp: int, date_format: str, expected_output: str):
        output = single_variable_output(f"{{%datetime_strftime({timestamp}, {date_format})}}")
        assert output == expected_output
