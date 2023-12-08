import re

import pytest

from ytdl_sub.script.script import Script
from ytdl_sub.script.script import ScriptBuilder
from ytdl_sub.script.types.map import Map
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import ScriptBuilderMissingDefinitions
from ytdl_sub.script.utils.exceptions import VariableDoesNotExist


class TestScriptBuilder:
    def test_partial_update_script(self):
        # to be resolved later
        entry_map = Map({String("title"): String("the title")})

        script = ScriptBuilder(
            {
                "entry": "{ {} }",
                "title": "{%map_get(entry, 'title', '')}",
                "resolved_override": "{override} mom",
            }
        )

        assert script.partial_build().resolve(unresolvable={"entry"})

        with pytest.raises(
            ScriptBuilderMissingDefinitions,
            match=re.escape("resolved_override is missing the following definitions: override"),
        ):
            script.build()

        script.add({"override": "hi"})
        script.add_resolved({"entry": entry_map})

        script.build()

        # script.resolve(unresolvable={"entry"}, update=True)
        # assert script.get("override") == String("hi")
        # assert script.get("resolved_override") == String("hi mom")
        #
        # script.add(
        #     {
        #         "new_variable_titlecase": "{%titlecase(new_variable_upper)}",
        #         "new_variable": "{resolved_override} {title}",
        #         "new_variable_upper": "{%upper(new_variable)}",
        #     }
        # ).resolve(resolved={"entry": entry_map}, update=True)
        #
        # assert script.get("title") == String("the title")
        # assert script.get("new_variable") == String("hi mom the title")
        # assert script.get("new_variable_upper") == String("HI MOM THE TITLE")
        # assert script.get("new_variable_titlecase") == String("Hi Mom The Title")
        # assert script.get("entry") == entry_map
