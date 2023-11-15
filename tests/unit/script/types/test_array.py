import re

import pytest

from ytdl_sub.script.parser import UNEXPECTED_CHAR_ARGUMENT
from ytdl_sub.script.parser import UNEXPECTED_COMMA_ARGUMENT
from ytdl_sub.script.parser import ArgumentParser
from ytdl_sub.script.script import Script
from ytdl_sub.script.types.array import ResolvedArray
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import InvalidSyntaxException


class TestArray:
    def test_return(self):
        assert Script({"array": "{['a', 3.14]}"}).resolve() == {
            "array": ResolvedArray([String("a"), Float(3.14)])
        }

    def test_return_as_str(self):
        assert Script({"array": "str: {['a', 3.14]}"}).resolve() == {
            "array": String('str: ["a", 3.14]')
        }

    @pytest.mark.parametrize(
        "array, expected_bool",
        [
            ("{%bool([])}", False),
            ("{%bool([False])}", True),
        ],
    )
    def test_return_as_bool(self, array: str, expected_bool: bool):
        assert Script({"array_as_bool": array}).resolve() == {
            "array_as_bool": Boolean(expected_bool)
        }

    def test_nested_array(self):
        assert Script(
            {"array": "{['level1', ['level2', ['level3', 'level3'], 'level2'], 'level1']}"}
        ).resolve() == {
            "array": ResolvedArray(
                [
                    String("level1"),
                    ResolvedArray(
                        [
                            String("level2"),
                            ResolvedArray([String("level3"), String("level3")]),
                            String("level2"),
                        ],
                    ),
                    String("level1"),
                ]
            )
        }

    @pytest.mark.parametrize(
        "array",
        [
            "{[]}",
            "{  []  }",
            "{  [    ] }",
            "{[\n]}",
        ],
    )
    def test_empty(self, array: str):
        assert Script({"array": array}).resolve() == {"array": ResolvedArray([])}

    @pytest.mark.parametrize(
        "array",
        [
            "{[,]}",
            "{[ ,]}",
            "{ [ , ]}",
            "{  ['test',]  }",
            "{  [   'test',  ] }",
            "{[\n,\n]}",
        ],
    )
    def test_unexpected_comma(self, array: str):
        with pytest.raises(
            InvalidSyntaxException,
            match=re.escape(str(UNEXPECTED_COMMA_ARGUMENT(ArgumentParser.ARRAY))),
        ):
            Script({"array": array}).resolve()

    @pytest.mark.parametrize(
        "array",
        [
            "{[}",
            "{[      }",
            "{[\n}",
            "{['key'}",
            "{[ 'key'   }",
        ],
    )
    def test_array_not_closed(self, array: str):
        with pytest.raises(
            InvalidSyntaxException,
            match=re.escape(str(UNEXPECTED_CHAR_ARGUMENT(ArgumentParser.ARRAY))),
        ):
            assert Script({"array": array}).resolve()

    @pytest.mark.parametrize(
        "array",
        [
            "{]}" "{      ]}",
            "{\n]}",
        ],
    )
    def test_array_not_opened(self, array: str):
        with pytest.raises(
            InvalidSyntaxException,
            match=re.escape(str(UNEXPECTED_CHAR_ARGUMENT(ArgumentParser.SCRIPT))),
        ):
            assert Script({"array": array}).resolve()

    def test_custom_function(self):
        assert Script(
            {
                "%custom_func": "return {[$1, $2]}",
                "aa": "a",
                "bb": "b",
                "cc": "{%custom_func(aa, bb)}",
            }
        ).resolve() == {"aa": String("a"), "bb": String("b"), "cc": String('return ["a", "b"]')}
