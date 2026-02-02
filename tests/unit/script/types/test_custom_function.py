import re

import pytest

from ytdl_sub.script.parser import CUSTOM_FUNCTION_ARGUMENTS_ONLY_ARGS
from ytdl_sub.script.script import Script
from ytdl_sub.script.script_output import ScriptOutput
from ytdl_sub.script.types.function import CustomFunction
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.utils.exceptions import CycleDetected
from ytdl_sub.script.utils.exceptions import FunctionDoesNotExist
from ytdl_sub.script.utils.exceptions import InvalidCustomFunctionArgumentName
from ytdl_sub.script.utils.exceptions import InvalidCustomFunctionArguments
from ytdl_sub.script.utils.exceptions import InvalidSyntaxException


class TestCustomFunction:
    def test_custom_function_use_input_param_multiple_times(self):
        assert Script(
            {
                "%custom_square": "{%mul($0, $0)}",
                "output": "{%custom_square(3)}",
            }
        ).resolve() == ScriptOutput({"output": Integer(9)})

    def test_custom_functions_any_order_via_add(self):
        assert Script({}).add(
            {
                "%custom_cubed": "{%mul(%custom_square($0),$0)}",
                "%custom_square": "{%mul($0, $0)}",
                "output": "{%custom_cubed(3)}",
            }
        ).resolve() == ScriptOutput({"output": Integer(27)})

    def test_custom_functions_any_order_via_init(self):
        assert Script(
            {
                "%custom_cubed": "{%mul(%custom_square($0),$0)}",
                "%custom_square": "{%mul($0, $0)}",
                "output": "{%custom_cubed(3)}",
            }
        ).resolve() == ScriptOutput({"output": Integer(27)})

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
    def test_custom_function_invalid_function_argument_names(self, name: str):
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

    def test_custom_function_function_argument_usage_in_brackets(self):
        with pytest.raises(
            InvalidSyntaxException,
            match=re.escape(str(CUSTOM_FUNCTION_ARGUMENTS_ONLY_ARGS)),
        ):
            Script({"%func1": "{$0}"}).resolve()

    @pytest.mark.parametrize(
        "argument",
        [
            "$1",
            "$2",
            "$3",
        ],
    )
    def test_custom_function_invalid_function_argument_single(self, argument: str):
        with pytest.raises(
            InvalidCustomFunctionArguments,
            match=re.escape(
                f"Custom function %func1 has invalid function arguments: "
                f"The argument must start with $0, not {argument}."
            ),
        ):
            Script(
                {
                    "%func1": f"{{[{argument}]}}",
                }
            ).resolve()

    @pytest.mark.parametrize(
        "arguments",
        [
            "$0, $2",
            "$1, $2, $3",
        ],
    )
    def test_custom_function_invalid_function_argument_out_of_order(self, arguments: str):
        with pytest.raises(
            InvalidCustomFunctionArguments,
            match=re.escape(
                f"Custom function %func1 has invalid function arguments: "
                f"{arguments} do not increment from $0 to ${len(arguments.split(',')) - 1}."
            ),
        ):
            Script(
                {
                    "%func1": f"{{[{arguments}]}}",
                }
            ).resolve()

    def test_custom_function_uses_custom_function_wrong_number_of_arguments(self):
        with pytest.raises(
            InvalidCustomFunctionArguments,
            match=re.escape(
                "Custom function %func0 has invalid usage of the custom function %func1: "
                "Expects 1 argument but received 2"
            ),
        ):
            Script(
                {
                    "%func1": "{%mul(1, $0)}",
                    "%func0": "{%mul(%func1(1, 2), $0)}",
                    "output": "{%func0(1)}",
                }
            ).resolve()

    def test_custom_function_uses_custom_function_wrong_number_of_arguments_plural(self):
        with pytest.raises(
            InvalidCustomFunctionArguments,
            match=re.escape(
                "Custom function %func0 has invalid usage of the custom function %func1: "
                "Expects 2 arguments but received 1"
            ),
        ):
            Script(
                {
                    "%func1": "{%mul($1, $0)}",
                    "%func0": "{%mul(%func1(1), $0)}",
                    "output": "{%func0(1)}",
                }
            ).resolve()

    def test_variable_uses_custom_function_wrong_number_of_arguments(self):
        with pytest.raises(
            InvalidCustomFunctionArguments,
            match=re.escape(
                "Variable output has invalid usage of the custom function %func1: "
                "Expects 1 argument but received 2"
            ),
        ):
            Script(
                {
                    "%func1": "{%mul(1, $0)}",
                    "output": "{%mul(%func1(1, 2), 1)}",
                }
            ).resolve()

    def test_variable_uses_custom_function_wrong_number_of_arguments_plural(self):
        with pytest.raises(
            InvalidCustomFunctionArguments,
            match=re.escape(
                "Variable output has invalid usage of the custom function %func1: "
                "Expects 2 arguments but received 1"
            ),
        ):
            Script(
                {
                    "%func1": "{%mul($1, $0)}",
                    "output": "{%mul(%func1(1), 1)}",
                }
            ).resolve()

    def test_function_argument_errors_has_spaces(self):
        with pytest.raises(
            InvalidCustomFunctionArgumentName,
            match=re.escape(
                "Custom function arguments, denoted by $, cannot have a space proceeding it."
            ),
        ):
            Script(
                {
                    "%func1": "{%mul($ 1, $0)}",
                    "output": "{%mul(%func1(1), 1)}",
                }
            )

    def test_partial_resolve_custom_functions_any_order_via_init(self):
        assert (
            Script(
                {
                    "%custom_cubed": "{%mul(%custom_square($0),$0)}",
                    "%custom_square": "{%mul($0, $0)}",
                    "output": "{%custom_cubed(3)}",
                }
            )
            .resolve_partial()
            .get("output")
            .native
            == 27
        )

    def test_partial_resolve_unresolved(self):
        assert Script(
            {
                "aa": "nope",
                "%custom_cubed": "{%mul(%custom_square($0),$0)}",
                "%custom_square": "{%mul($0, aa)}",
                "output": "{%custom_cubed(3)}",
            }
        ).resolve_partial(unresolvable={"aa"}).definition_of("output") == SyntaxTree(
            ast=[CustomFunction(name="custom_cubed", args=[Integer(3)])]
        )
