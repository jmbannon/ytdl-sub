from typing import Union

import pytest

from ytdl_sub.script.parser import parse
from ytdl_sub.script.syntax_tree import SyntaxTree
from ytdl_sub.script.types.function import Function
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.variable import Variable
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

    def test_array(self):
        parsed = parse("hello {['elem1', 'elem2']}")
        parsed_empty = parse("hello {[]}")
        parsed_with_var = parse("hello {['elem1', variable_name]}")
        parsed_extend = parse("hi {%extend(['elem1', 'elem2'], ['elem3'], [],   ['elem4'])}")
        assert False

    def test_map(self):
        parsed = parse("hello {%map(['elem1', 'elem2'])}")
        parsed_empty = parse("hello {%map()}")
        parsed_with_var = parse("hello {%map([variable_name, 'elem2'])}")
        parsed_extend = parse("hi {%map([variable_name, 'elem2'], ['elem3', variable_name])}")
        parsed_extend.resolve({})
        assert False

    def test_conditional(self):
        parsed = parse("hello {%if(True, 'hi', 3.4)}")
        assert parsed == SyntaxTree(
            [
                String("hello "),
                Function(
                    name="if", args=[Boolean(value=True), String(value="hi"), Float(value=3.4)]
                ),
            ]
        )
        assert parsed.ast[1].output_type == Union[String, Float]

    def test_conditional_as_input_same_outputs(self):
        parsed = parse("hello {%concat(%if(True, 'hi', 'mom'), 'and dad')}")
        assert parsed == SyntaxTree(
            [
                String("hello "),
                Function(
                    name="concat",
                    args=[
                        Function(
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
                Function(
                    name="string",
                    args=[
                        Function(name="if", args=[Boolean(True), String("hi"), Integer(4)]),
                    ],
                ),
            ]
        )

    def test_single_function_one_vararg(self):
        parsed = parse("hello {%concat('hi mom')}")
        assert parsed == SyntaxTree(
            [
                String("hello "),
                Function(name="concat", args=[String(value="hi mom")]),
            ]
        )

    def test_single_function_many_vararg(self):
        parsed = parse("hello {%concat('hi', 'mom')}")
        assert parsed == SyntaxTree(
            [
                String("hello "),
                Function(name="concat", args=[String(value="hi"), String(value="mom")]),
            ]
        )

    def test_single_function_many_args_with_optional_none(self):
        parsed = parse("hello {%replace('hi mom', 'hi', '')}")
        assert parsed == SyntaxTree(
            [
                String("hello "),
                Function(
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
                Function(
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

    @pytest.mark.parametrize("whitespace", ["", " ", "  ", "\n", " \n "])
    def test_single_function_multiple_args(self, whitespace: str):
        s = whitespace
        parsed = parse(
            f"hello{s}{{{s}%concat({s}'string'{s},{s}%string(1){s},{s}%string(2.4){s},"
            f"{s}%string(TRUE){s},{s}%string(variable_name){s},{s}%capitalize({s}'hi'{s}){s}){s}}}"
        )
        assert parsed == SyntaxTree(
            [
                String(value=f"hello{s}"),
                Function(
                    name="concat",
                    args=[
                        String(value="string"),
                        Function(name="string", args=[Integer(value=1)]),
                        Function(name="string", args=[Float(value=2.4)]),
                        Function(name="string", args=[Boolean(value=True)]),
                        Function(name="string", args=[Variable(name="variable_name")]),
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
