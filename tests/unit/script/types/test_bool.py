import re

import pytest

from ytdl_sub.script.parser import BOOLEAN_ONLY_ARGS
from ytdl_sub.script.script import Script
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import InvalidSyntaxException


class TestBool:
    @pytest.mark.parametrize(
        "boolean",
        [
            "{True}",
            "{  True  }",
            "{False}",
            "{  False  }",
        ],
    )
    def test_boolean_not_arg(self, boolean: str):
        with pytest.raises(InvalidSyntaxException, match=re.escape(str(BOOLEAN_ONLY_ARGS))):
            Script({"boolean": boolean}).resolve()

    @pytest.mark.parametrize(
        "boolean, expected_boolean",
        [
            ("{%bool(True)}", True),
            ("{%bool(False)}", False),
            ("{%bool(    True   )}", True),
            ("{%bool(   False   )}", False),
        ],
    )
    def test_boolean(self, boolean: bool, expected_boolean: bool):
        assert Script({"boolean": boolean, "as_string": "{%string(boolean)}"}).resolve() == {
            "boolean": Boolean(expected_boolean),
            "as_string": String(str(expected_boolean)),
        }

    @pytest.mark.parametrize(
        "to_cast, expected_bool",
        [
            ("{%bool(False)}", False),
            ("{%bool(True)}", True),
            ("{%bool(0)}", False),
            ("{%bool(1)}", True),
            ("{%bool(0.0)}", False),
            ("{%bool(0.1)}", True),
            ("{%bool('')}", False),
            ("{%bool('false')}", True),
            ("{%bool([])}", False),
            ("{%bool([False])}", True),
            ("{%bool({})}", False),
            ("{%bool({'key': 'value'})}", True),
        ],
    )
    def test_cast_as_bool(self, to_cast: str, expected_bool: bool):
        assert Script({"as_bool": to_cast}).resolve() == {"as_bool": Boolean(expected_bool)}
