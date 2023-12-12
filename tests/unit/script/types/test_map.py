import re

import pytest

from ytdl_sub.script.parser import _UNEXPECTED_COMMA_ARGUMENT
from ytdl_sub.script.parser import BRACKET_NOT_CLOSED
from ytdl_sub.script.parser import MAP_KEY_MULTIPLE_VALUES
from ytdl_sub.script.parser import MAP_KEY_NOT_HASHABLE
from ytdl_sub.script.parser import MAP_KEY_WITH_NO_VALUE
from ytdl_sub.script.parser import MAP_MISSING_KEY
from ytdl_sub.script.parser import ParsedArgType
from ytdl_sub.script.script import Script
from ytdl_sub.script.script_output import ScriptOutput
from ytdl_sub.script.types.map import Map
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import InvalidSyntaxException
from ytdl_sub.script.utils.exceptions import KeyNotHashableRuntimeException


class TestMap:
    def test_return(self):
        assert Script({"dict": "{{'a': 3.14}}"}).resolve() == ScriptOutput(
            {"dict": Map({String("a"): Float(3.14)})}
        )

    def test_return_as_str(self):
        assert Script({"dict": "json: {{'a': 3.14}}"}).resolve() == ScriptOutput(
            {"dict": String('json: {"a": 3.14}')}
        )

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

        assert Script({"dict": map_str}).resolve() == ScriptOutput(
            {
                "dict": Map(
                    {
                        String("level1"): Map(
                            {
                                String("level2"): Map(
                                    {
                                        String("level3"): Map(
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
        )

    @pytest.mark.parametrize(
        "empty_map",
        [
            "{{}}",
            "{{ }}",
            "{{      }}",
            "{{\n}}",
        ],
    )
    def test_empty_map(self, empty_map: str):
        assert Script({"dict": empty_map}).resolve() == ScriptOutput({"dict": Map({})})

    @pytest.mark.parametrize(
        "map",
        [
            "{{}",
            "{{      }",
            "{{\n}",
            "{{'key': 'value'}",
            "{{ 'key' : 'value' }",
            "{{      }",
        ],
    )
    def test_map_not_closed(self, map: str):
        with pytest.raises(InvalidSyntaxException, match=re.escape(str(BRACKET_NOT_CLOSED))):
            Script({"dict": map}).resolve()

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
        with pytest.raises(InvalidSyntaxException, match=re.escape(str(MAP_KEY_WITH_NO_VALUE))):
            Script({"dict": value}).resolve()

    @pytest.mark.parametrize(
        "value",
        [
            "{{,}}",
            "{{ , }}",
            "{{'key':'value',,}}",
            "{{'key': 'value', ,}}",
        ],
    )
    def test_map_unexpected_comma(self, value: str):
        with pytest.raises(
            InvalidSyntaxException,
            match=re.escape(str(_UNEXPECTED_COMMA_ARGUMENT(ParsedArgType.MAP_KEY))),
        ):
            Script({"dict": value}).resolve()

    @pytest.mark.parametrize(
        "value",
        [
            "{{'key1','key2'}}",
            "{{'key1'     , 'key2'}}",
            "{{ 'key1', 'key2': 'value' }}",
        ],
    )
    def test_map_multiple_keys(self, value: str):
        with pytest.raises(InvalidSyntaxException, match=re.escape(str(MAP_KEY_MULTIPLE_VALUES))):
            Script({"dict": value}).resolve()

    @pytest.mark.parametrize(
        "value",
        [
            "{{:}}",
            "{{  :  }}",
            "{{  : 'value' }}",
        ],
    )
    def test_map_missing_key(self, value: str):
        with pytest.raises(InvalidSyntaxException, match=re.escape(str(MAP_MISSING_KEY))):
            Script({"dict": value}).resolve()

    @pytest.mark.parametrize(
        "value",
        [
            "{{{}:'value'}}",
            "{{ {} : 'value' }}",
            "{{[]:'value'}}",
            "{{ [] : 'value' }}",
        ],
    )
    def test_map_key_not_hashable(self, value: str):
        with pytest.raises(InvalidSyntaxException, match=re.escape(str(MAP_KEY_NOT_HASHABLE))):
            Script({"dict": value}).resolve()

    def test_map_key_is_hashable_variable(self):
        assert Script(
            {
                "dict": "{{key_variable : 'value' }}",
                "key_variable": "hashable",
            }
        ).resolve() == ScriptOutput(
            {
                "key_variable": String("hashable"),
                "dict": Map({String("hashable"): String("value")}),
            }
        )

    def test_map_key_is_non_hashable_variable(self):
        with pytest.raises(
            KeyNotHashableRuntimeException,
            match=re.escape("Tried to use Array as a Map key, but it is not hashable."),
        ):
            Script(
                {
                    "dict": "{{key_variable : 'value' }}",
                    "key_variable": "{['non-hashable']}",
                }
            ).resolve()
