import copy
from abc import ABC
from typing import Any
from typing import Dict
from typing import Set

from ytdl_sub.entries.script.function_scripts import CUSTOM_FUNCTION_SCRIPTS
from ytdl_sub.entries.script.variable_scripts import UNRESOLVED_VARIABLES
from ytdl_sub.entries.script.variable_scripts import VARIABLE_SCRIPTS
from ytdl_sub.script.script import Script
from ytdl_sub.utils.script import ScriptUtils


class Scriptable(ABC):
    def __init__(self):
        self.script = Script(
            ScriptUtils.add_sanitized_variables(
                dict(copy.deepcopy(VARIABLE_SCRIPTS), **copy.deepcopy(CUSTOM_FUNCTION_SCRIPTS))
            )
        )
        self.unresolvable: Set[str] = copy.deepcopy(UNRESOLVED_VARIABLES)

    def update_script(self) -> None:
        self.script.resolve(unresolvable=self.unresolvable, update=True)

    def add(self, values: Dict[str, Any]) -> None:
        self.unresolvable -= set(list(values.keys()))
        self.script.add(
            ScriptUtils.add_sanitized_variables(
                {name: ScriptUtils.to_script(value) for name, value in values.items()}
            ),
            unresolvable=self.unresolvable,
        )
        self.update_script()
