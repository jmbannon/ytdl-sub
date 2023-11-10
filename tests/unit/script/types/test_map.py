import re

import pytest

from ytdl_sub.script.script import Script
from ytdl_sub.script.types.map import ResolvedMap
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import InvalidSyntaxException


class TestMap:
    def test_return(self):
        assert Script({"map": "{{'a': 3.14}}"}).resolve() == {
            "map": ResolvedMap({String("a"): Float(3.14)})
        }

    def test_return_as_str(self):
        assert Script({"map": "json: {{'a': 3.14}}"}).resolve() == {
            "map": String('json: {"a": 3.14}')
        }

    def test_nested_map(self):
        map_str = """{
            {
                'level1': {
                    'level2': {
                        'level3': {
                            'level4_key': 'level4_value'
                        },
                        'level3_key': 'level3_value'
                    },
                    'level2_key': 'level2_value'
                },
                'level1_key': 'level1_value'
            }
        }"""

        assert Script({"map": map_str}).resolve() == {
            "map": ResolvedMap(
                {
                    String("level1"): ResolvedMap(
                        {
                            String("level2"): ResolvedMap(
                                {
                                    String("level3"): ResolvedMap(
                                        {String("level4_key"): String("level4_value")}
                                    ),
                                    String("level3_key"): String("level3_value"),
                                }
                            ),
                            String("level2_key"): String("level2_value"),
                        }
                    ),
                    String("level1_key"): String("level1_value"),
                }
            )
        }

    def test_empty_map(self):
        assert Script({"map": "{{}}"}).resolve() == {"map": ResolvedMap({})}

    @pytest.mark.parametrize(
        "value",
        [
            "{{'key': }}",
            "{{'key':}}",
            "{{'key': 'value', 'key2':}}",
            "{{'key': 'value', 'key2': }}",
            "{{    'key': 'value', 'key2':\n}}",
            "{{    'key': ,\n}}",
        ],
    )
    def test_key_has_no_value(self, value: str):
        # with pytest.raises(InvalidSyntaxException, match=re.escape("Map has a key with no value")):
        Script({"map": value}).resolve()
