import re

import pytest

from ytdl_sub.script.script import Script
from ytdl_sub.script.types.array import ResolvedArray
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.utils.exceptions import CycleDetected


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
