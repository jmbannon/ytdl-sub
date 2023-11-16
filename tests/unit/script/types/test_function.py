import re
from typing import Tuple

import pytest

from ytdl_sub.script.parser import NUMERICS_INVALID_CHAR
from ytdl_sub.script.parser import NUMERICS_ONLY_ARGS
from ytdl_sub.script.parser import STRINGS_ONLY_ARGS
from ytdl_sub.script.parser import UNEXPECTED_CHAR_ARGUMENT
from ytdl_sub.script.parser import UNEXPECTED_COMMA_ARGUMENT
from ytdl_sub.script.parser import ArgumentParser
from ytdl_sub.script.script import Script
from ytdl_sub.script.types.array import ResolvedArray
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import IncompatibleFunctionArguments
from ytdl_sub.script.utils.exceptions import InvalidSyntaxException


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
                expected="Map, Hashable, Optional", recieved="%if(...)->Union[Map, Array], String"
            ),
        ):
            Script({"func": function_str}).resolve()

    @pytest.mark.parametrize(
        "function_str", ["{%array_at({'a': 'dict?'}, 1)}" "{%array_extend('not', 'array')}"]
    )
    def test_incompatible_types(self, function_str):
        assert Script({"func": function_str}).resolve()
