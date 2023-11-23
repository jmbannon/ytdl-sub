from ytdl_sub.script.script import Script
from ytdl_sub.script.types.map import ResolvedMap
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
        ).resolve(unresolvable={"bb"}) == {"aa": String("a")}

    def test_partial_update_script(self):
        script = Script(
            {
                "entry": "{%throw('entry has not been populated yet')}",
                "title": "{%map_get(entry, 'title')}",
                "override": "hi",
            }
        )

        overrides = script.resolve(unresolvable={"entry"})
        assert overrides == {"override": String("hi")}

        entry_map = ResolvedMap({String("title"): String("the title")})
        entry_output = script.resolve(
            pre_resolved_variables=dict(overrides, **{"entry": entry_map})
        )
        assert entry_output == {
            "override": String("hi"),
            "entry": entry_map,
            "title": String("the title"),
        }
