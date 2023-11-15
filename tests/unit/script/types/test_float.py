import re
from typing import Tuple

import pytest

from ytdl_sub.script.parser import NUMERICS_INVALID_CHAR
from ytdl_sub.script.parser import NUMERICS_ONLY_ARGS
from ytdl_sub.script.parser import UNEXPECTED_CHAR_ARGUMENT
from ytdl_sub.script.parser import UNEXPECTED_COMMA_ARGUMENT
from ytdl_sub.script.parser import ArgumentParser
from ytdl_sub.script.script import Script
from ytdl_sub.script.types.array import ResolvedArray
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import InvalidSyntaxException


class TestFloat:
    @pytest.mark.parametrize(
        "integer",
        [
            "{1.0}",
            "{  1.2  }",
            "{-1.4}",
            "{   -1.5   }",
            "{0001.2}",
            "{  0001.5   }",
        ],
    )
    def test_float_not_arg(self, integer: str):
        with pytest.raises(InvalidSyntaxException, match=re.escape(str(NUMERICS_ONLY_ARGS))):
            Script({"float": integer}).resolve()

    @pytest.mark.parametrize(
        "float_, expected_float",
        [
            ("{%float(1.1)}", 1.1),
            ("{%float(  1.2345  )}", 1.2345),
            ("{%float(-1.34)}", -1.34),
            ("{%float(   -1.535   )}", -1.535),
            ("{%float(0001.)}", 1.0),
            ("{%float(  0001.   )}", 1.0),
        ],
    )
    def test_float(self, float_: str, expected_float: int):
        assert Script({"float": float_, "as_string": "{%string(float)}"}).resolve() == {
            "float": Float(expected_float),
            "as_string": String(str(expected_float)),
        }

    @pytest.mark.parametrize(
        "float_, expected_bool",
        [
            ("{%bool(0.0)}", False),
            ("{%bool(0.1)}", True),
        ],
    )
    def test_return_as_bool(self, float_: str, expected_bool: bool):
        assert Script({"as_bool": float_}).resolve() == {"as_bool": Boolean(expected_bool)}

    @pytest.mark.parametrize(
        "float_",
        [
            "{%add(0, --1.0)}",
            "{%add(0,  1-.0  )}",
            "{%add(0,-1.0.)}",
            "{%add(0,   -1.0.   )}",
            "{%add(0,0001.a)}",
            "{%add(0,  0001.-   )}",
        ],
    )
    def test_invalid_float(self, float_: str):
        with pytest.raises(InvalidSyntaxException, match=re.escape(str(NUMERICS_INVALID_CHAR))):
            Script({"float": float_}).resolve()
