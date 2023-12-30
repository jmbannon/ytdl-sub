import json

import pytest
from unit.script.conftest import single_variable_output


class TestJsonFunctions:
    @pytest.mark.parametrize("str_token", ["'''", '"""'])
    def test_from_json(self, str_token: str):
        json_dict = {
            "string": "value",
            "quotes": "has '' and \"\"",
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

        output = single_variable_output(
            f"{{ %from_json({str_token}{json.dumps(json_dict)}{str_token}) }}"
        )
        assert output == json_dict
