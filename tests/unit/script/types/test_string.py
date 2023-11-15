import re
from typing import Tuple

import pytest

from ytdl_sub.script.parser import NUMERICS_INVALID_CHAR
from ytdl_sub.script.parser import NUMERICS_ONLY_ARGS
from ytdl_sub.script.parser import STRINGS_ONLY_ARGS
from ytdl_sub.script.parser import UNEXPECTED_CHAR_ARGUMENT
from ytdl_sub.script.parser import UNEXPECTED_COMMA_ARGUMENT
from ytdl_sub.script.parser import ArgumentParser
from ytdl_sub.script.script import Script
from ytdl_sub.script.types.array import ResolvedArray
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import InvalidSyntaxException


class TestString:
    @pytest.mark.parametrize(
        "string",
        [
            "{'323'}",
            '{  "4253"  }',
            '{"hi"}',
            '{   "asfsd"   }',
            '{"sdfasf"}',
            "{  '3fsdf'   }",
        ],
    )
    def test_string_not_arg(self, string: str):
        with pytest.raises(InvalidSyntaxException, match=re.escape(str(STRINGS_ONLY_ARGS))):
            Script({"string": string}).resolve()
