from ytdl_sub.script.script import Script
from ytdl_sub.script.types.resolvable import String


class TestScript:
    def test_pre_resolved(self):
        assert Script(
            {
                "%custom_func": "return {[$0, $1]}",
                "aa": "a",
                "bb": "b",
                "cc": "{%custom_func(aa, bb)}",
            }
        ).resolve(pre_resolved_variables={"bb": String("bb_override")}) == {
            "aa": String("a"),
            "bb": String("bb_override"),
            "cc": String('return ["a", "bb_override"]'),
        }

    def test_partial_resolve(self):
        assert Script(
            {
                "%custom_func": "return {[$0, $1]}",
                "aa": "a",
                "bb": "b",
                "cc": "{%custom_func(aa, bb)}",
            }
        ).partial_resolve(unresolvable={"bb"}) == {"aa": String("a")}
