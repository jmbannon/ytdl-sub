import re

import pytest

from ytdl_sub.script.parser import FUNCTION_INVALID_CHAR
from ytdl_sub.script.script import Script
from ytdl_sub.script.types.array import ResolvedArray
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import String
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

    def test_lambda_function(self):
        assert Script(
            {"%times_two": "{%mul($0, 2)}", "wip": "{%array_apply([1, 2, 3], %times_two)}"}
        ).resolve() == {"wip": ResolvedArray([Integer(2), Integer(4), Integer(6)])}
