import re

import pytest

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
        output = (
            Script({"output": "{%assert(['a'], 'test this error message')}"})
            .resolve(update=True)
            .get("output")
            .native
        )

        assert output == ["a"]
