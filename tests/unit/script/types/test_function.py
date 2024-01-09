import re

import pytest
from unit.script.conftest import single_variable_output

from ytdl_sub.script.functions import Functions
from ytdl_sub.script.parser import FUNCTION_INVALID_CHAR
from ytdl_sub.script.script import Script
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.utils.exceptions import FunctionDoesNotExist
from ytdl_sub.script.utils.exceptions import FunctionRuntimeException
from ytdl_sub.script.utils.exceptions import IncompatibleFunctionArguments
from ytdl_sub.script.utils.exceptions import InvalidSyntaxException


def _incompatible_arguments_match(expected: str, recieved: str) -> str:
    return re.escape(f"Expected ({expected})\nReceived ({recieved})")


def mock_register_function(integer: Integer) -> Integer:
    return Integer(integer.value + 100)


class TestFunction:
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
                expected="mapping: Map, key: AnyArgument, default: Optional[AnyArgument]",
                recieved="%if(...)->Union[Array, Map], String",
            ),
        ):
            Script({"func": function_str}).resolve()

    @pytest.mark.parametrize(
        "function_str, expected_types, received_types",
        [
            (
                "{%array_at({'a': 'dict?'}, 1)}",
                "array: Array, idx: Integer, default: Optional[AnyArgument]",
                "Map, Integer",
            ),
            ("{%array_extend('not', 'array')}", "arrays: Array, ...", "String, String"),
            (
                "{%replace('hi mom', 'mom', 'dad', 1, 0)}",
                "string: String, old: String, new: String, count: Optional[Integer]",
                "String, String, String, Integer, Integer",
            ),
        ],
    )
    def test_incompatible_types(self, function_str: str, expected_types: str, received_types: str):
        with pytest.raises(
            IncompatibleFunctionArguments,
            match=_incompatible_arguments_match(expected=expected_types, recieved=received_types),
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

    def test_register_function(self):
        try:
            Functions.register_function(function=mock_register_function)
            output = single_variable_output(f"{{%mock_register_function(10)}}")
            assert output == 110
        finally:
            del Functions._custom_functions[mock_register_function.__name__]
