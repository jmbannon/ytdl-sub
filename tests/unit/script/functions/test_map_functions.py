import re

import pytest

from ytdl_sub.script.script import Script
from ytdl_sub.script.utils.exceptions import KeyDoesNotExistRuntimeException


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
