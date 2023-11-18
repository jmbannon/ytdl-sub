import re
from typing import Optional
from typing import Union

import pytest

from ytdl_sub.script.parser import _UNEXPECTED_CHAR_ARGUMENT
from ytdl_sub.script.parser import BRACKET_NOT_CLOSED
from ytdl_sub.script.parser import ParsedArgType
from ytdl_sub.script.parser import parse
from ytdl_sub.script.types.function import BuiltInFunction
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exceptions import InvalidSyntaxException
from ytdl_sub.utils.exceptions import StringFormattingException


class TestParser:
    def test_simple(self):
        parsed = parse("hello world")
        assert parsed == SyntaxTree([String(value="hello world")])
        assert parsed.variables == set()

    def test_single_function_one_arg(self):
        parsed = parse("hello {%capitalize('hi mom')}")
        assert parsed == SyntaxTree(
            [
                String("hello "),
                BuiltInFunction(name="capitalize", args=[String(value="hi mom")]),
            ]
        )

    def test_conditional(self):
        parsed = parse("hello {%if(True, 'hi', 3.4)}")
        assert parsed == SyntaxTree(
            [
                String("hello "),
                BuiltInFunction(
                    name="if", args=[Boolean(value=True), String(value="hi"), Float(value=3.4)]
                ),
            ]
        )
        assert parsed.ast[1].output_type() == Union[String, Float]

    def test_conditional_as_input_same_outputs(self):
        parsed = parse("hello {%concat(%if(True, 'hi', 'mom'), 'and dad')}")
        assert parsed == SyntaxTree(
            [
                String("hello "),
                BuiltInFunction(
                    name="concat",
                    args=[
                        BuiltInFunction(
                            name="if", args=[Boolean(value=True), String("hi"), String("mom")]
                        ),
                        String(value="and dad"),
                    ],
                ),
            ]
        )

    def test_conditional_as_input_different_outputs(self):
        parsed = parse("hello {%string(%if(True, 'hi', 4))}")
        assert parsed == SyntaxTree(
            [
                String("hello "),
                BuiltInFunction(
                    name="string",
                    args=[
                        BuiltInFunction(name="if", args=[Boolean(True), String("hi"), Integer(4)]),
                    ],
                ),
            ]
        )

    def test_single_function_one_vararg(self):
        parsed = parse("hello {%concat('hi mom')}")
        assert parsed == SyntaxTree(
            [
                String("hello "),
                BuiltInFunction(name="concat", args=[String(value="hi mom")]),
            ]
        )

    def test_single_function_many_vararg(self):
        parsed = parse("hello {%concat('hi', 'mom')}")
        assert parsed == SyntaxTree(
            [
                String("hello "),
                BuiltInFunction(name="concat", args=[String(value="hi"), String(value="mom")]),
            ]
        )

    def test_single_function_many_args_with_optional_none(self):
        parsed = parse("hello {%replace('hi mom', 'hi', '')}")
        assert parsed == SyntaxTree(
            [
                String("hello "),
                BuiltInFunction(
                    name="replace",
                    args=[String(value="hi mom"), String(value="hi"), String(value="")],
                ),
            ]
        )

    def test_single_function_many_args_with_optional_provided(self):
        parsed = parse("hello {%replace('hi mom', 'hi', '', 1)}")
        assert parsed == SyntaxTree(
            [
                String("hello "),
                BuiltInFunction(
                    name="replace",
                    args=[
                        String(value="hi mom"),
                        String(value="hi"),
                        String(value=""),
                        Integer(value=1),
                    ],
                ),
            ]
        )

    @pytest.mark.parametrize("whitespace", [None, " ", "  ", "\n", " \n "])
    def test_single_function_multiple_args(self, whitespace: Optional[str]):
        s = whitespace
        if s is None:
            s = ""

        input_str = (
            f"hello{s}{{{s}%concat({s}'string'{s},{s}%string(1){s},{s}%string(2.4){s},"
            f"{s}%string(True){s},{s}%string(variable_name){s},{s}%capitalize({s}'hi'{s}){s})}}"
            f"{s}"
        )
        parsed = parse(input_str)
        assert parsed == SyntaxTree(
            [
                String(value=f"hello{s}"),
                BuiltInFunction(
                    name="concat",
                    args=[
                        String(value="string"),
                        BuiltInFunction(name="string", args=[Integer(value=1)]),
                        BuiltInFunction(name="string", args=[Float(value=2.4)]),
                        BuiltInFunction(name="string", args=[Boolean(value=True)]),
                        BuiltInFunction(name="string", args=[Variable(name="variable_name")]),
                        BuiltInFunction(name="capitalize", args=[String(value="hi")]),
                    ],
                ),
            ]
            + ([String(value=s)] if s else [])
        )
        assert parsed.variables == {Variable(name="variable_name")}


class TestParserBracketFailures:
    def test_bracket_open(self):
        with pytest.raises(StringFormattingException):
            parse("{")

    def test_bracket_close(self):
        with pytest.raises(InvalidSyntaxException, match=re.escape(str(BRACKET_NOT_CLOSED))):
            parse("}")

    def test_bracket_in_function(self):
        with pytest.raises(
            InvalidSyntaxException,
            match=re.escape(str(_UNEXPECTED_CHAR_ARGUMENT(ParsedArgType.MAP_KEY))),
        ):
            parse("hello {%capitalize({as_arg)}")
