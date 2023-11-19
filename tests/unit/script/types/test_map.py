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
from ytdl_sub.script.types.map import ResolvedMap
from ytdl_sub.script.types.resolvable import Boolean
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
        assert Script({"map": empty_map}).resolve() == {"map": ResolvedMap({})}

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
            Script({"map": map}).resolve()

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
            Script({"map": value}).resolve()

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
            Script({"map": value}).resolve()

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
            Script({"map": value}).resolve()

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
            Script({"map": value}).resolve()

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
            Script({"map": value}).resolve()
