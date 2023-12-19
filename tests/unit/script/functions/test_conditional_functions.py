import pytest

from ytdl_sub.script.script import Script


class TestConditionalFunction:
    @pytest.mark.parametrize(
        "function_str, expected_output",
        [
            ("{%if(True, True, False)}", True),
            ("{%if(False, True, False)}", False),
        ],
    )
    def test_if_function(self, function_str: str, expected_output: bool):
        output = Script({"output": function_str}).resolve(update=True).get("output").native
        assert output == expected_output

    def test_nested_if_function(self):
        function_str = """{
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
        output = Script({"output": function_str}).resolve(update=True).get("output").native
        assert output == "winner"
