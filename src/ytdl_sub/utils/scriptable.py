from abc import ABC
from typing import Dict
from typing import Set

from ytdl_sub.entries.script.variable_scripts import VARIABLE_SCRIPTS
from ytdl_sub.script.script import Script


class Scriptable(ABC):
    @classmethod
    def add_sanitized_variables(cls, variables: Dict[str, str]) -> Dict[str, str]:
        sanitized_variables = {
            f"{name}_sanitized": f"{{%sanitize({name})}}" for name in variables.keys()
        }
        return dict(variables, **sanitized_variables)

    def __init__(self):
        self.script = Script(VARIABLE_SCRIPTS)
        self.unresolvable: Set[str] = set()

    def update_script(self) -> None:
        self.script.resolve(unresolvable=self.unresolvable, update=True)
