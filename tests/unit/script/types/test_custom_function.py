import re

import pytest

from ytdl_sub.script.script import Script
from ytdl_sub.script.types.array import ResolvedArray
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.utils.exceptions import CycleDetected
from ytdl_sub.script.utils.exceptions import FunctionDoesNotExist
from ytdl_sub.script.utils.exceptions import InvalidCustomFunctionArgumentName


class TestCustomFunction:
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
                "Cycle detected within these custom functions: "
                "%cycle_func1 -> %cycle_func0 -> %cycle_func1"
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
                "Cycle detected within these custom functions: "
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

    def test_custom_function_uses_non_existent_function(self):
        with pytest.raises(
            FunctionDoesNotExist,
            match=re.escape("Function %lolnope does not exist as a built-in or custom function."),
        ):
            Script(
                {
                    "%func1": "{%mul(%lolnope(1), $0)}",
                    "%func0": "{%mul(%func1(1), $0)}",
                    "output": "{%func(1)}",
                }
            ).resolve()

    @pytest.mark.parametrize(
        "name",
        [
            "$00invalid",
            "$abc",
            "$3.14",
        ],
    )
    def test_custom_function_invalid_function_arguments(self, name: str):
        with pytest.raises(
            InvalidCustomFunctionArgumentName,
            match=re.escape(
                "Custom function arguments must be numeric and increment starting from zero."
            ),
        ):
            Script(
                {
                    "%func1": f"{{%mul(1, {name})}}",
                    "%func0": "{%mul(%func1(1), $0)}",
                    "output": "{%func0(1)}",
                }
            ).resolve()
