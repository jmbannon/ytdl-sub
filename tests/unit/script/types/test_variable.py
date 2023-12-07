import re

import pytest

from ytdl_sub.script.script import Script
from ytdl_sub.script.script_output import ScriptOutput
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import CycleDetected
from ytdl_sub.script.utils.exceptions import InvalidVariableName
from ytdl_sub.script.utils.exceptions import VariableDoesNotExist


class TestVariable:
    def test_simple(self):
        assert Script({"a": "a", "b": "{b_}", "b_": "b"}).resolve() == ScriptOutput(
            {
                "a": String("a"),
                "b": String("b"),
                "b_": String("b"),
            }
        )

    def test_multiple_variables(self):
        assert Script({"a": "a", "b": "b", "b_": "  {a}  {b}  "}).resolve() == ScriptOutput(
            {
                "a": String("a"),
                "b": String("b"),
                "b_": String("  a  b  "),
            }
        )

    def test_simple_with_function(self):
        assert Script({"a": "a", "b": "{%capitalize(b_)}", "b_": "b"}).resolve() == ScriptOutput(
            {
                "a": String("a"),
                "b": String("B"),
                "b_": String("b"),
            }
        )

    def test_simple_cycle(self):
        with pytest.raises(
            CycleDetected,
            match=re.escape("Cycle detected within these variables: a -> b -> a"),
        ):
            Script({"a": "{b}", "b": "{a}"}).resolve()

    def test_simple_cycle_with_function(self):
        with pytest.raises(
            CycleDetected,
            match=re.escape("Cycle detected within these variables: b -> b_ -> b"),
        ):
            Script({"b": "{%capitalize(b_)}", "b_": "{b}"}).resolve()

    def test_undefined_variable(self):
        with pytest.raises(
            VariableDoesNotExist,
            match=re.escape("Variable c does not exist."),
        ):
            Script({"a": "a", "b": "{c}"}).resolve()

    @pytest.mark.parametrize(
        "name",
        [
            "vali_LOL_INVALID",
            "name!!",
            "na(",
            "na[",
        ],
    )
    def test_invalid_variable_name_inline(self, name: str):
        with pytest.raises(
            InvalidVariableName,
            match=re.escape(
                f"Variable name '{name}' is invalid:"
                " Names must be lower_snake_cased and begin with a letter."
            ),
        ):
            Script({"a": f"{{{name}}}"}).resolve()

    @pytest.mark.parametrize(
        "name",
        ["float", "bool", "mul"],
    )
    def test_invalid_variable_name_inline_is_built_in(self, name: str):
        with pytest.raises(
            InvalidVariableName,
            match=re.escape(
                f"Variable name '{name}' is invalid:"
                " The name is used by a built-in function and cannot be overwritten."
            ),
        ):
            Script({"a": f"{{{name}}}"}).resolve()

    @pytest.mark.parametrize(
        "name",
        [
            "vali_LOL_INVALID",
            "name!!",
            "na(",
            "na[",
            "$2232",
            "1245",
            "CAN_CATCH_MORE",
            "{brackets_in_definition}",
        ],
    )
    def test_invalid_variable_name_definition(self, name: str):
        with pytest.raises(
            InvalidVariableName,
            match=re.escape(
                f"Variable name '{name}' is invalid:"
                " Names must be lower_snake_cased and begin with a letter."
            ),
        ):
            Script({f"{name}": "value"}).resolve()

    @pytest.mark.parametrize(
        "name",
        ["float", "bool", "mul"],
    )
    def test_invalid_variable_name_definition_is_built_in(self, name: str):
        with pytest.raises(
            InvalidVariableName,
            match=re.escape(
                f"Variable name '{name}' is invalid:"
                " The name is used by a built-in function and cannot be overwritten."
            ),
        ):
            Script({f"{name}": "value"}).resolve()
