from ytdl_sub.script.script import Script
from ytdl_sub.script.types.array import ResolvedArray
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import String


class TestArray:
    def test_return(self):
        assert Script({"array": "{['a', 3.14]}"}).resolve() == {
            "array": ResolvedArray([String("a"), Float(3.14)])
        }

    def test_return_as_str(self):
        assert Script({"array": "str: {['a', 3.14]}"}).resolve() == {
            "array": String("str: [a, 3.14]")
        }

    def test_nested_array(self):
        assert Script(
            {"array": "{['level1', ['level2', ['level3', 'level3'], 'level2'], 'level1']}"}
        ).resolve() == {
            "array": ResolvedArray(
                [
                    String("level1"),
                    ResolvedArray(
                        [
                            String("level2"),
                            ResolvedArray([String("level3"), String("level3")]),
                            String("level2"),
                        ],
                    ),
                    String("level1"),
                ]
            )
        }

    def test_empty_array(self):
        assert Script({"array": "{[]}"}).resolve() == {"array": ResolvedArray([])}

    def test_custom_function(self):
        assert Script(
            {
                "%custom_func": "return {[$1, $2]}",
                "aa": "a",
                "bb": "b",
                "cc": "{%custom_func(aa, bb)}",
            }
        ).resolve() == {"aa": String("a"), "bb": String("b"), "cc": String("return [a, b]")}
