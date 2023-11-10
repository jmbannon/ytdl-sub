from typing import Dict

import pytest

from ytdl_sub.script.script import Script
from ytdl_sub.script.syntax_tree import SyntaxTree
from ytdl_sub.script.types.function import Function
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.utils.exceptions import StringFormattingException


class TestSyntaxTree:
    def test_custom_function(self):
        assert Script(
            {
                "%custom_func": "return {[$1, $2]}",
                "aa": "a",
                "bb": "b",
                "cc": "{%custom_func(aa, bb)}",
            }
        ).resolve() == {"aa": String("a"), "bb": String("b"), "cc": String("return [aa, bb]")}

    def test_simple(self):
        assert Script({"a": "a", "b": "{b_}", "b_": "b",}).resolve() == {
            "a": String("a"),
            "b": String("b"),
            "b_": String("b"),
        }

    def test_simple_with_function(self):
        assert Script({"a": "a", "b": "{%capitalize(b_)}", "b_": "b",}).resolve() == {
            "a": String("a"),
            "b": String("B"),
            "b_": String("b"),
        }

    def test_simple_cycle(self):
        with pytest.raises(StringFormattingException):
            Script({"a": "{b}", "b": "{a}"}).resolve()

    def test_simple_cycle_with_function(self):
        with pytest.raises(StringFormattingException):
            Script({"b": "{%capitalize(b_)}", "b_": "{b}"}).resolve()
