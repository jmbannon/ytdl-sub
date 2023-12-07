import re

import pytest
from unit.script.conftest import single_variable_output

from ytdl_sub.script.script import Script
from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError


class TestErrorFunctions:
    def test_user_throw(self):
        with pytest.raises(UserThrownRuntimeError, match=re.escape("test this error message")):
            Script({"throw_error": "{%throw('test this error message')}"}).resolve()

    def test_user_assert_raises(self):
        with pytest.raises(UserThrownRuntimeError, match=re.escape("test this error message")):
            Script({"throw_error": "{%assert(False, 'test this error message')}"}).resolve()

    def test_user_assert_passthrough(self):
        output = single_variable_output("{%assert(['a'], 'test this error message')}")
        assert output == ["a"]

    def test_user_assert_passthrough_as_arg(self):
        output = single_variable_output("{%int(%assert('123', 'test this error message'))}")
        assert output == 123
