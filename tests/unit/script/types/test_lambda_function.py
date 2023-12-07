import re

import pytest

from ytdl_sub.script.script import Script
from ytdl_sub.script.script_output import ScriptOutput
from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.utils.exceptions import IncompatibleFunctionArguments


class TestLambdaFunction:
    def test_lambda_with_custom_function(self):
        assert Script(
            {"%times_two": "{%mul($0, 2)}", "wip": "{%array_apply([1, 2, 3], %times_two)}"}
        ).resolve() == ScriptOutput({"wip": Array([Integer(2), Integer(4), Integer(6)])})

    def test_conditional_lambda_with_custom_functions(self):
        assert Script(
            {
                "%times_three": "{%mul($0, 3)}",
                "%times_two": "{%mul($0, 2)}",
                "wip": "{%array_apply([1, 2, 3], %if(False, %times_two, %times_three))}",
            }
        ).resolve() == ScriptOutput({"wip": Array([Integer(3), Integer(6), Integer(9)])})

    def test_nested_custom_functions(self):
        assert Script(
            {
                "%times_three": "{%mul($0, 3)}",
                "%times_two": "{%mul($0, 2)}",
                "identity": "{%times_three(%times_two(1))}",
            }
        ).resolve() == ScriptOutput({"identity": Integer(6)})

    def test_nested_custom_functions_within_custom_functions(self):
        assert Script(
            {
                "%power_2": "{%mul($0, 2)}",
                "%power_3": "{%mul(%power_2($0), 2)}",
                "%power_4": "{%mul(%power_3($0), 2)}",
                "power_of_4": "{%power_4(2)}",
            }
        ).resolve() == ScriptOutput({"power_of_4": Integer(16)})

    def test_nested_lambda_custom_functions_within_custom_functions(self):
        assert Script(
            {
                "%nest4": "{%mul($0, 2)}",
                "%nest3": "{%array_at(%array_apply([$0], %nest4), 0)}",
                "%nest2": "{%array_at(%array_apply([$0], %nest3), 0)}",
                "%nest1": "{%array_at(%array_apply([$0], %nest2), 0)}",
                "output": "{%array_at(%array_apply([2], %nest1), 0)}",
            }
        ).resolve() == ScriptOutput({"output": Integer(4)})


class TestLambdaFunctionIncompatibleNumArguments:
    @pytest.mark.parametrize(
        "lambda_value", ["%enumerate_output", "%if(False, %capitalize, %enumerate_output)"]
    )
    def test_custom_function_lambda_in_variable(self, lambda_value: str):
        with pytest.raises(
            IncompatibleFunctionArguments,
            match=re.escape(
                "Variable output has invalid usage of the custom function "
                "%enumerate_output as a lambda: Expects 2 arguments but will receive 1."
            ),
        ):
            Script(
                {
                    "%enumerate_output": "{[$0, $1]}",
                    "array1": "{['a', 'b', 'c']}",
                    "output": f"{{%array_apply(array1, {lambda_value})}}",
                }
            )

    @pytest.mark.parametrize("lambda_value", ["%replace", "%if(False, %capitalize, %replace)"])
    def test_function_lambda_in_variable(self, lambda_value: str):
        with pytest.raises(
            IncompatibleFunctionArguments,
            match=re.escape(
                "Variable output has invalid usage of the function %replace as a lambda: "
                "Expects 3 - 4 arguments but will receive 1."
            ),
        ):
            Script(
                {
                    "array1": "{['a', 'b', 'c']}",
                    "output": f"{{%array_apply(array1, {lambda_value})}}",
                }
            )

    @pytest.mark.parametrize(
        "lambda_value", ["%enumerate_output", "%if(False, %concat, %enumerate_output)"]
    )
    def test_custom_function_lambda_in_custom_function(self, lambda_value: str):
        with pytest.raises(
            IncompatibleFunctionArguments,
            match=re.escape(
                "Custom function %output has invalid usage of the custom function "
                "%enumerate_output as a lambda: Expects 3 arguments but will receive 2."
            ),
        ):
            Script(
                {
                    "%enumerate_output": "{[$0, $1, $2]}",
                    "array1": "{['a', 'b', 'c']}",
                    "%output": f"{{%array_enumerate(array1, {lambda_value})}}",
                }
            )

    @pytest.mark.parametrize("lambda_value", ["%replace", "%if(False, %concat, %replace)"])
    def test_function_lambda_in_custom_function(self, lambda_value: str):
        with pytest.raises(
            IncompatibleFunctionArguments,
            match=re.escape(
                "Custom function %output has invalid usage of the function "
                "%replace as a lambda: Expects 3 - 4 arguments but will receive 2."
            ),
        ):
            Script(
                {
                    "array1": "{['a', 'b', 'c']}",
                    "%output": f"{{%array_enumerate(array1, {lambda_value})}}",
                }
            )
