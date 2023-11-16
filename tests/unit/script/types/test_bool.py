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
