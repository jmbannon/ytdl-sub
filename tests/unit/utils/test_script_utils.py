import copy

import pytest
from unit.script.conftest import single_variable_output

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
