import re

import pytest

from ytdl_sub.script.script import Script
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import CycleDetected


class TestSyntaxTree:
    def test_custom_function(self):
        assert Script(
            {
                "%custom_func": "return {[$0, $1]}",
                "aa": "a",
                "bb": "b",
                "cc": "{%custom_func(aa, bb)}",
            }
        ).resolve() == {"aa": String("a"), "bb": String("b"), "cc": String('return ["a", "b"]')}

    def test_simple(self):
        assert Script({"a": "a", "b": "{b_}", "b_": "b"}).resolve() == {
            "a": String("a"),
            "b": String("b"),
            "b_": String("b"),
        }

    def test_multiple_variables(self):
        assert Script({"a": "a", "b": "b", "b_": "  {a}  {b}  "}).resolve() == {
            "a": String("a"),
            "b": String("b"),
            "b_": String("  a  b  "),
        }

    def test_simple_with_function(self):
        assert Script({"a": "a", "b": "{%capitalize(b_)}", "b_": "b"}).resolve() == {
            "a": String("a"),
            "b": String("B"),
            "b_": String("b"),
        }

    def test_simple_cycle(self):
        with pytest.raises(
            CycleDetected,
            match=re.escape("Cycle detected within these variables: " "a -> b -> a"),
        ):
            Script({"a": "{b}", "b": "{a}"}).resolve()

    def test_simple_cycle_with_function(self):
        with pytest.raises(
            CycleDetected,
            match=re.escape("Cycle detected within these variables: " "b -> b_ -> b"),
        ):
            Script({"b": "{%capitalize(b_)}", "b_": "{b}"}).resolve()
