import pytest

from ytdl_sub.script.parser import Boolean
from ytdl_sub.script.parser import Float
from ytdl_sub.script.parser import Function
from ytdl_sub.script.parser import Integer
from ytdl_sub.script.parser import LiteralString
from ytdl_sub.script.parser import Parser
from ytdl_sub.script.parser import String
from ytdl_sub.script.parser import Variable
from ytdl_sub.utils.exceptions import StringFormattingException


class TestParser:
    def test_simple(self):
        parser = Parser("hello world").parse()
        assert list(parser._stack.queue) == [LiteralString(value="hello world")]

    def test_single_function_one_arg(self):
        parser = Parser("hello {%capitalize('hi mom')}").parse()
        assert list(parser._stack.queue) == [
            LiteralString("hello "),
            Function(name="capitalize", args=[String(value="hi mom")]),
        ]

    @pytest.mark.parametrize('whitespace', ["", " ", "  ", "\n", " \n "])
    def test_single_function_multiple_args(self, whitespace: str):
        s = whitespace
        parser = Parser(
            f"hello{s}{{{s}%concat({s}'string'{s},{s}1{s},{s}2.4{s},"
            f"{s}TRUE{s},{s}variable_name{s},{s}%capitalize({s}'hi'{s}){s}){s}}}"
        ).parse()
        assert list(parser._stack.queue) == [
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
        ] + ([LiteralString(value=s)] if s else [])


class TestParserBracketFailures:
    def test_bracket_open(self):
        with pytest.raises(StringFormattingException):
            _ = Parser("{").parse()

    def test_bracket_close(self):
        with pytest.raises(StringFormattingException):
            _ = Parser("}").parse()

    def test_bracket_in_function(self):
        with pytest.raises(StringFormattingException):
            _ = Parser("hello {%capitalize({as_arg)}").parse()
