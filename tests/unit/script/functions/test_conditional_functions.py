import re

import pytest
from unit.script.conftest import single_variable_output

from ytdl_sub.script.utils.exceptions import FunctionRuntimeException


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

    def test_elif_function(self):
        output = single_variable_output(
            """{
            %elif(
                False,
                "nope",
                False,
                "still nope",
                True,
                "yes",
                "default value"
            )
        }"""
        )
        assert output == "yes"

    def test_elif_function_default_value(self):
        output = single_variable_output(
            """{
            %elif(
                False,
                "nope",
                False,
                "still nope",
                False,
                "will be default",
                "default value"
            )
        }"""
        )
        assert output == "default value"

    def test_elif_function_errors_lt3(self):
        with pytest.raises(
            FunctionRuntimeException,
            match=re.escape("elif requires at least 3 arguments"),
        ):
            single_variable_output(
                """
            {
                %elif(
                    False,
                    "only two args"
                )
            }"""
            )

    def test_elif_function_errors_odd(self):
        with pytest.raises(
            FunctionRuntimeException,
            match=re.escape("elif must have an odd number of arguments"),
        ):
            single_variable_output(
                """
            {
                %elif(
                    False,
                    "1",
                    False,
                    "even number args bad"
                )
            }"""
            )
