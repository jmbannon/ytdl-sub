from typing import Dict

import pytest

from ytdl_sub.script.syntax_tree import SyntaxTree
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.utils.exceptions import StringFormattingException


class TestSyntaxTree:
    def test_simple(self):
        overrides: Dict[str, SyntaxTree] = {
            "a": SyntaxTree(ast=[String("a")]),
            "b": SyntaxTree(ast=[Variable("b_")]),
            "b_": SyntaxTree(ast=[String("b")]),
        }

        resolved = SyntaxTree.resolve_overrides(parsed_overrides=overrides)
        assert resolved == {
            "a": String(value="a"),
            "b": String(value="b"),
            "b_": String(value="b"),
        }

    def test_simple_cycle(self):
        overrides: Dict[str, SyntaxTree] = {
            "a": SyntaxTree(ast=[Variable("b")]),
            "b": SyntaxTree(ast=[Variable("a")]),
        }

        with pytest.raises(StringFormattingException):
            _ = SyntaxTree.resolve_overrides(parsed_overrides=overrides)
