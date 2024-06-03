import copy

import pytest
from unit.script.conftest import single_variable_output

from ytdl_sub.script.parser import parse
from ytdl_sub.script.types.function import BuiltInFunction
from ytdl_sub.script.types.map import UnresolvedMap
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.utils.script import ScriptUtils


class TestScriptUtils:
    def test_dict_to_script(self):
        json_dict = {
            "string": "value",
            "quotes": "has '' and \"\"",
            "triple-single-quote": "right here! '''''''''''''''''''''''''''''' ack '''''''",
            "int": 1,
            "bool": True,
            "list": [1, 2, 3],
            "dict": {"a": 1, "b": 2},
            "float": 3.14,
            "nested_dict": {
                "string": "value",
                "int": 1,
                "bool": True,
                "list": [1, 2, 3],
                "dict": {"a": 1, "b": 2},
                "float": 3.14,
            },
        }

        expected_output = copy.deepcopy(json_dict)
        expected_output["triple-single-quote"] = "right here! ' ack '"

        output = single_variable_output(ScriptUtils.to_script(json_dict))
        assert output == expected_output

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("", False),
            ("true", True),
            ("false", False),
            ("[    ]", False),
            ("{    }", False),
            ("True", True),
            ("False", False),
            ("lol not False", True),
            ("0", False),
            ("-1", True),
            ("1", True),
        ],
    )
    def test_bool_formatter_output(self, input_str: str, expected_output: bool):
        assert ScriptUtils.bool_formatter_output(input_str) == expected_output

    def test_to_syntax_tree(self):
        out = ScriptUtils.to_native_script(
            {"{var_a}": "{var_b}", "static_a": "string with {var_c} in it"}
        )
        assert parse(out) == SyntaxTree(
            ast=[
                UnresolvedMap(
                    value={
                        Variable(name="var_a"): Variable(name="var_b"),
                        String(value="static_a"): BuiltInFunction(
                            name="concat",
                            args=[
                                BuiltInFunction(name="string", args=[String(value="string with ")]),
                                BuiltInFunction(name="string", args=[Variable(name="var_c")]),
                                BuiltInFunction(name="string", args=[String(value=" in it")]),
                            ],
                        ),
                    }
                )
            ]
        )
