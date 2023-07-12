import pytest

from ytdl_sub.script.parser import parse
from ytdl_sub.script.types import Boolean
from ytdl_sub.script.types import Float
from ytdl_sub.script.types import Function
from ytdl_sub.script.types import Integer
from ytdl_sub.script.types import LiteralString
from ytdl_sub.script.types import String
from ytdl_sub.script.types import SyntaxTree
from ytdl_sub.script.types import Variable
from ytdl_sub.utils.exceptions import StringFormattingException


class TestParser:
    def test_simple(self):
        assert parse("hello world") == SyntaxTree([LiteralString(value="hello world")])

    def test_single_function_one_arg(self):
        assert parse("hello {%capitalize('hi mom')}") == SyntaxTree(
            [
                LiteralString("hello "),
                Function(name="capitalize", args=[String(value="hi mom")]),
            ]
        )

    @pytest.mark.parametrize("whitespace", ["", " ", "  ", "\n", " \n "])
    def test_single_function_multiple_args(self, whitespace: str):
        s = whitespace
        assert parse(
            f"hello{s}{{{s}%concat({s}'string'{s},{s}1{s},{s}2.4{s},"
            f"{s}TRUE{s},{s}variable_name{s},{s}%capitalize({s}'hi'{s}){s}){s}}}"
        ) == SyntaxTree(
            [
                LiteralString(value=f"hello{s}"),
                Function(
                    name="concat",
                    args=[
                        String(value="string"),
                        Integer(value=1),
                        Float(value=2.4),
                        Boolean(value=True),
                        Variable(name="variable_name"),
                        Function(name="capitalize", args=[String(value="hi")]),
                    ],
                ),
            ]
            + ([LiteralString(value=s)] if s else [])
        )


class TestParserBracketFailures:
    def test_bracket_open(self):
        with pytest.raises(StringFormattingException):
            parse("{")

    def test_bracket_close(self):
        with pytest.raises(StringFormattingException):
            parse("}")

    def test_bracket_in_function(self):
        with pytest.raises(StringFormattingException):
            parse("hello {%capitalize({as_arg)}")
