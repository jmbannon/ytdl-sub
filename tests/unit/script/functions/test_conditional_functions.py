import pytest
from unit.script.conftest import single_variable_output


class TestConditionalFunction:
    @pytest.mark.parametrize(
        "function_str, expected_output",
        [
            ("{%if(True, True, False)}", True),
            ("{%if(False, True, False)}", False),
        ],
    )
    def test_if_function(self, function_str: str, expected_output: bool):
        output = single_variable_output(function_str)
        assert output == expected_output

    def test_nested_if_function(self):
        output = single_variable_output(
            """{
            %if(
                True,
                %if(
                    True,
                    %if(
                        True,
                        "winner",
                        True
                    ),
                    True
                ),
                True
            )
        }"""
        )
        assert output == "winner"
