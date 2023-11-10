from typing import Dict

import pytest

from ytdl_sub.script.script import Script
from ytdl_sub.script.syntax_tree import SyntaxTree
from ytdl_sub.script.types.function import Function
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.utils.exceptions import StringFormattingException


class TestSyntaxTree:
    def test_simple(self):
        script = Script(
            {
                "a": "a",
                "b": "{b_}",
                "b_": "b",
            }
        )

    def test_custom_function(self):
        script = Script(
            {
                "%custom_func": "return {[$1, $2]}",
                "aa": "a",
                "bb": "b",
                "cc": "{%custom_func(aa, bb)}",
            }
        )

        out = script.resolve()
        assert False



