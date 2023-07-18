import pytest

from ytdl_sub.script.functions import Boolean
from ytdl_sub.script.functions import Float
from ytdl_sub.script.functions import Integer
from ytdl_sub.script.functions import String
from ytdl_sub.script.parser import parse
from ytdl_sub.script.syntax_tree import Function
from ytdl_sub.script.syntax_tree import SyntaxTree
from ytdl_sub.script.syntax_tree import Variable
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
                Function(name="capitalize", args=[String(value="hi mom")]),
            ]
        )

    @pytest.mark.parametrize("whitespace", ["", " ", "  ", "\n", " \n "])
    def test_single_function_multiple_args(self, whitespace: str):
        s = whitespace
        parsed = parse(
            f"hello{s}{{{s}%concat({s}'string'{s},{s}1{s},{s}2.4{s},"
            f"{s}TRUE{s},{s}variable_name{s},{s}%capitalize({s}'hi'{s}){s}){s}}}"
        )
        assert parsed == SyntaxTree(
            [
                String(value=f"hello{s}"),
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
            + ([String(value=s)] if s else [])
        )
        assert parsed.variables == {Variable(name="variable_name")}


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
