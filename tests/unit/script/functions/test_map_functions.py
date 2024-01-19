import re

import pytest
from unit.script.conftest import single_variable_output

from ytdl_sub.script.script import Script
from ytdl_sub.script.utils.exceptions import FunctionRuntimeException
from ytdl_sub.script.utils.exceptions import KeyDoesNotExistRuntimeException
from ytdl_sub.script.utils.exceptions import KeyNotHashableRuntimeException


class TestMapFunctions:
    def test_map_get(self):
        output = (
            Script(
                {
                    "input_map": "{{'key': 'value'}}",
                    "output": "{%map_get(input_map, 'key')}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == "value"

    def test_map_get_optional(self):
        output = (
            Script(
                {
                    "input_map": "{{'key': 'value'}}",
                    "output": "{%map_get(input_map, 'dne', 'optional_value')}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == "optional_value"

    def test_map_get_errors_missing_key(self):
        with pytest.raises(
            KeyDoesNotExistRuntimeException,
            match=re.escape("Tried to call %map_get with key dne, but it does not exist"),
        ):
            Script(
                {
                    "input_map": "{{'key': 'value'}}",
                    "output": "{%map_get(input_map, 'dne')}",
                }
            ).resolve()

    def test_map_get_errors_key_not_hashable(self):
        with pytest.raises(
            KeyNotHashableRuntimeException,
            match=re.escape("Tried to use Array as a Map key, but it is not hashable."),
        ):
            Script(
                {
                    "non_hashable_key": "{%array([1, 2, ['nest']])}",
                    "input_map": "{{'key': 'value'}}",
                    "output": "{ %map_get( input_map, %array_at(non_hashable_key, 2)) }",
                }
            ).resolve()

    @pytest.mark.parametrize(
        "contains_value, expected_value",
        [
            ("'key'", True),
            ("'dne'", False),
            ("%string(%array_at(['dne', 'key'], 1))", True),
        ],
    )
    def test_map_contains(self, contains_value: str, expected_value: bool):
        output = (
            Script(
                {
                    "input_map": "{{'key': 'value'}}",
                    "output": f"{{%map_contains(input_map, {contains_value})}}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == expected_value

    def test_map_apply(self):
        output = (
            Script(
                {
                    "%custom_func": "{[%upper($0), %lower($1)]}",
                    "map1": "{{'Key1': 'Value1', 'Key2': 'Value2'}}",
                    "output": "{%map_apply(map1, %custom_func)}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == [["KEY1", "value1"], ["KEY2", "value2"]]

    def test_map_enumerate(self):
        output = (
            Script(
                {
                    "%custom_func": "{[$0, %upper($1), %lower($2)]}",
                    "map1": "{{'Key1': 'Value1', 'Key2': 'Value2'}}",
                    "output": "{%map_enumerate(map1, %custom_func)}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == [[0, "KEY1", "value1"], [1, "KEY2", "value2"]]

    def test_map_size(self):
        output = single_variable_output("{%map_size({'key': 'value', 1: 3})}")
        assert output == 2

    def test_cast_map(self):
        output = (
            Script(
                {
                    "array_test": "{ [1, 2, {'key': 'value'}] }",
                    "output": "{ %map( %array_at(array_test, 2) )}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == {"key": "value"}

    def test_cast_map_errors_cannot_cast(self):
        with pytest.raises(
            FunctionRuntimeException, match="Tried and failed to cast Integer as a Map"
        ):
            single_variable_output("{%map(1)}")

    def test_map_extend(self):
        output = single_variable_output("""{
            %map_extend(
              {'key': 'value', 1: 3},
              {'key': 'override'}
              {'new': [1, 2]}
            )
        }""")
        assert output == {'key': 'override', 'new': [1, 2], 1: 3}