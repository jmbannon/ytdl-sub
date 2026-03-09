import re

import pytest
from unit.script.conftest import single_variable_output

from ytdl_sub.script.script import Script
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exceptions import FunctionRuntimeException


class TestConditionalFunction:
    @pytest.mark.parametrize(
        "function_str, expected_output",
        [
            ("{%if(True, True, False)}", True),
            ("{%if(False, True, False)}", False),
        ],
    )
    def test_if_function(self, function_str: str, expected_output: bool):
        output = single_variable_output(function_str)
        assert output == expected_output

    def test_nested_if_function(self):
        output = single_variable_output(
            """{
            %if(
                True,
                %if(
                    True,
                    %if(
                        True,
                        "winner",
                        True
                    ),
                    True
                ),
                True
            )
        }"""
        )
        assert output == "winner"

    def test_elif_function(self):
        output = single_variable_output(
            """{
            %elif(
                False,
                "nope",
                False,
                "still nope",
                True,
                "yes",
                "default value"
            )
        }"""
        )
        assert output == "yes"

    def test_elif_function_default_value(self):
        output = single_variable_output(
            """{
            %elif(
                False,
                "nope",
                False,
                "still nope",
                False,
                "will be default",
                "default value"
            )
        }"""
        )
        assert output == "default value"

    def test_elif_function_errors_lt3(self):
        with pytest.raises(
            FunctionRuntimeException,
            match=re.escape("elif requires at least 3 arguments"),
        ):
            single_variable_output(
                """
            {
                %elif(
                    False,
                    "only two args"
                )
            }"""
            )

    def test_elif_function_errors_odd(self):
        with pytest.raises(
            FunctionRuntimeException,
            match=re.escape("elif must have an odd number of arguments"),
        ):
            single_variable_output(
                """
            {
                %elif(
                    False,
                    "1",
                    False,
                    "even number args bad"
                )
            }"""
            )

    @pytest.mark.parametrize(
        "function_str, expected_output",
        [
            ("{%if(True, True, %assert(False, 'should not reach'))}", True),
            ("{%if(False, %assert(False, 'should not reach'), False)}", False),
        ],
    )
    def test_if_function_only_evaluates_branch(self, function_str: str, expected_output: bool):
        output = single_variable_output(function_str)
        assert output == expected_output

    @pytest.mark.parametrize(
        "function_str, expected_output",
        [
            ("{%elif(True, True, %assert(False, 'should not reach'))}", True),
            ("{%elif(False, %assert(False, 'should not reach'), False)}", False),
        ],
    )
    def test_elif_function_only_evaluates_branch(self, function_str: str, expected_output: bool):
        output = single_variable_output(function_str)
        assert output == expected_output

    @pytest.mark.parametrize(
        "function_str, expected_output",
        [
            ("{%if_passthrough(True, %assert(False, 'should not reach'))}", True),
        ],
    )
    def test_if_passthrough_function_only_evaluates_branch(
        self, function_str: str, expected_output: bool
    ):
        output = single_variable_output(function_str)
        assert output == expected_output

    def test_if_partial_resolve(self):
        assert (
            Script(
                {
                    "aa": "a",
                    "bb": "unresolvable!",
                    "cc": "{%if( true, aa, bb )}",
                }
            )
            .resolve_partial(unresolvable={"bb"})
            .get("cc")
            .native
            == "a"
        )

    def test_if_partial_resolve_unresolved(self):
        assert Script(
            {
                "aa": "a",
                "bb": "unresolvable!",
                "cc": "{%if( false, aa, bb )}",
            }
        ).resolve_partial(unresolvable={"bb"}).definition_of("cc") == SyntaxTree(
            ast=[Variable("bb")]
        )
