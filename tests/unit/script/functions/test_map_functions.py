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