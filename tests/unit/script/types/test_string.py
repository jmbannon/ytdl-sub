import re

import pytest

from unit.script.conftest import single_variable_output
from ytdl_sub.script.parser import STRINGS_NOT_CLOSED
from ytdl_sub.script.parser import STRINGS_ONLY_ARGS
from ytdl_sub.script.script import Script
from ytdl_sub.script.script_output import ScriptOutput
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
            Script({"out": string}).resolve()

    @pytest.mark.parametrize(
        "string, expected_string",
        [
            ("{%string('')}", ""),
            ('{%string("")}', ""),
            ('{%string("\\")}', "\\"),
            ("{%string('323')}", "323"),
            ('{%string(  "4253"  )}', "4253"),
            ('{%string("hi")}', "hi"),
            ('{%string(   "asfsd"   )}', "asfsd"),
            ('{%string("sdfasf")}', "sdfasf"),
            ("{%string(  '3fsdf'   )}", "3fsdf"),
            ("{%string('newlines \n newlines')}", "newlines \n newlines"),
            ("{%string('in function')} out of function", "in function out of function"),
            ("{%string('supports \" in string')}", 'supports " in string'),
            ('{%string("supports \' in string")}', "supports ' in string"),
            ("{%string('backslash \\\\')}", "backslash \\\\"),
            ("{%string('''triple quote with \" ' \\''')}", "triple quote with \" ' \\"),
            ('{%string("""triple quote with " \' \\""")}', "triple quote with \" ' \\"),
            ("{%string('literal \\n newlines')}", "literal \n newlines"),
            ("{%string('supports \t tabs')}", "supports \t tabs"),
            ("{%string('literal \\t tabs')}", "literal \t tabs"),
        ],
    )
    def test_string(self, string: str, expected_string: str):
        assert single_variable_output(string) == expected_string

    def test_null_is_empty_string(self):
        assert Script({"out": "{%string(null)}"}).resolve() == ScriptOutput({"out": String("")})

    @pytest.mark.parametrize(
        "string",
        [
            "{%string('open only single)}",
            '{%string(  "open only double  )}',
            "{%string(\"open double close single ')}",
            "{%string(  'open single close double\"   )}",
        ],
    )
    def test_string_not_closed_properly(self, string: str):
        with pytest.raises(InvalidSyntaxException, match=re.escape(str(STRINGS_NOT_CLOSED))):
            Script({"out": string}).resolve()
