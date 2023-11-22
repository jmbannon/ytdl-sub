import re

import pytest

from ytdl_sub.script.parser import FUNCTION_INVALID_CHAR
from ytdl_sub.script.script import Script
from ytdl_sub.script.types.array import ResolvedArray
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import CycleDetected
from ytdl_sub.script.utils.exceptions import FunctionDoesNotExist
from ytdl_sub.script.utils.exceptions import FunctionRuntimeException
from ytdl_sub.script.utils.exceptions import IncompatibleFunctionArguments
from ytdl_sub.script.utils.exceptions import InvalidSyntaxException
from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError


def _incompatible_arguments_match(expected: str, recieved: str) -> str:
    return re.escape(f"Expected ({expected})\nReceived ({recieved})")


class TestFunction:
    @pytest.mark.parametrize(
        "function_str, expected_output",
        [
            ("{%if(True, True, False)}", True),
            ("{%if(False, True, False)}", False),
        ],
    )
    def test_if_function(self, function_str: str, expected_output: bool):
        assert Script({"func": function_str}).resolve() == {
            "func": Boolean(expected_output),
        }

    def test_nested_if_function(self):
        function_str = """{
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
        assert Script({"func": function_str}).resolve() == {
            "func": String("winner"),
        }

    def test_nested_if_function_incompatible(self):
        function_str = """{
            %map_get(
                %if(
                    True,
                    %if(
                        True,
                        {},
                        []
                    ),
                    {}
                ),
                "key"
            )
        }"""
        with pytest.raises(
            IncompatibleFunctionArguments,
            match=_incompatible_arguments_match(
                expected="Map, Hashable, Optional[AnyType]",
                recieved="%if(...)->Union[Map, Array], String",
            ),
        ):
            Script({"func": function_str}).resolve()

    @pytest.mark.parametrize(
        "function_str", ["{%array_at({'a': 'dict?'}, 1)}" "{%array_extend('not', 'array')}"]
    )
    def test_incompatible_types(self, function_str):
        with pytest.raises(
            IncompatibleFunctionArguments,
            match=_incompatible_arguments_match(expected="Array, Integer", recieved="Map, Integer"),
        ):
            Script({"func": function_str}).resolve()

    def test_runtime_error(self):
        with pytest.raises(
            FunctionRuntimeException,
            match=re.escape(
                "Runtime error occurred when executing the function %div: division by zero"
            ),
        ):
            Script({"divide_by_zero": "{%div(8820, 0)}"}).resolve()

    def test_user_throw(self):
        with pytest.raises(UserThrownRuntimeError, match=re.escape("test this error message")):
            Script({"throw_error": "{%throw('test this error message')}"}).resolve()

    def test_user_assert(self):
        with pytest.raises(UserThrownRuntimeError, match=re.escape("test this error message")):
            Script({"throw_error": "{%assert(False, 'test this error message')}"}).resolve()

    def test_function_does_not_exist(self):
        with pytest.raises(
            FunctionDoesNotExist,
            match=re.escape("Function %lolnope does not exist as a built-in or custom function."),
        ):
            Script({"dne": "{%lolnope(False, 'test this error message')}"}).resolve()

    def test_function_does_not_close(self):
        with pytest.raises(
            InvalidSyntaxException,
            match=re.escape(str(FUNCTION_INVALID_CHAR)),
        ):
            Script({"dne": "{%throw}"}).resolve()

    def test_custom_function_use_input_param_multiple_times(self):
        assert Script(
            {
                "%custom_square": "{%mul($0, $0)}",
                "output": "{%custom_square(3)}",
            }
        ).resolve() == {"output": Integer(9)}

    def test_custom_function_cycle(self):
        with pytest.raises(
            CycleDetected, match=re.escape("The custom function %cycle_func cannot call itself.")
        ):
            Script(
                {"%cycle_func": "{%mul(%cycle_func(1), $0)}", "output": "{%cycle_func(1)}"}
            ).resolve()

    def test_custom_function_chained_cycle(self):
        with pytest.raises(
            CycleDetected,
            match=re.escape(
                "Custom functions contain a cycle: %cycle_func1 -> %cycle_func0 -> %cycle_func1"
            ),
        ):
            Script(
                {
                    "%cycle_func1": "{%mul(%cycle_func0(1), $0)}",
                    "%cycle_func0": "{%mul(%cycle_func1(1), $0)}",
                    "output": "{%cycle_func0(1)}",
                }
            ).resolve()

    def test_custom_function_deep_chained_cycle(self):
        with pytest.raises(
            CycleDetected,
            match=re.escape(
                "Custom functions contain a cycle: "
                "%cycle_func4 -> "
                "%cycle_func0 -> "
                "%cycle_func1 -> "
                "%cycle_func2 -> "
                "%cycle_func3 -> "
                "%cycle_func4"
            ),
        ):
            Script(
                {
                    "%nested_safe_func": "{%mul($0, 1)}",
                    "%safe_func": "{%nested_safe_func($0, 1)}",
                    "%cycle_func4": "{%mul(%cycle_func0(1), %safe_func($0))}",
                    "%cycle_func3": "{%mul(%cycle_func4(1), %safe_func($0))}",
                    "%cycle_func2": "{%mul(%cycle_func3(1), %safe_func($0))}",
                    "%cycle_func1": "{%mul(%cycle_func2(1), %safe_func($0))}",
                    "%cycle_func0": "{%mul(%cycle_func1(1), %safe_func($0))}",
                    "output": "{%cycle_func0(1)}",
                }
            ).resolve()

    def test_lambda_with_custom_function(self):
        assert Script(
            {"%times_two": "{%mul($0, 2)}", "wip": "{%array_apply([1, 2, 3], %times_two)}"}
        ).resolve() == {"wip": ResolvedArray([Integer(2), Integer(4), Integer(6)])}

    def test_conditional_lambda_with_custom_functions(self):
        assert Script(
            {
                "%times_three": "{%mul($0, 3)}",
                "%times_two": "{%mul($0, 2)}",
                "wip": "{%array_apply([1, 2, 3], %if(False, %times_two, %times_three))}",
            }
        ).resolve() == {"wip": ResolvedArray([Integer(3), Integer(6), Integer(9)])}

    def test_nested_custom_functions(self):
        assert Script(
            {
                "%times_three": "{%mul($0, 3)}",
                "%times_two": "{%mul($0, 2)}",
                "identity": "{%times_three(%times_two(1))}",
            }
        ).resolve() == {"identity": Integer(6)}

    def test_nested_custom_functions_within_custom_functions(self):
        assert Script(
            {
                "%power_2": "{%mul($0, 2)}",
                "%power_3": "{%mul(%power_2($0), 2)}",
                "%power_4": "{%mul(%power_3($0), 2)}",
                "power_of_4": "{%power_4(2)}",
            }
        ).resolve() == {"power_of_4": Integer(16)}

    def test_nested_lambda_custom_functions_within_custom_functions(self):
        assert Script(
            {
                "%nest4": "{%mul($0, 2)}",
                "%nest3": "{%array_at(%array_apply([$0], %nest4), 0)}",
                "%nest2": "{%array_at(%array_apply([$0], %nest3), 0)}",
                "%nest1": "{%array_at(%array_apply([$0], %nest2), 0)}",
                "output": "{%array_at(%array_apply([2], %nest1), 0)}",
            }
        ).resolve() == {"output": Integer(4)}
