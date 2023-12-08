import json
from abc import ABC
from typing import Any
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

    @classmethod
    def to_script(cls, value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, int):
            return f"{{%int({value})}}"
        if isinstance(value, float):
            return f"{{%float({value})}}"
        if isinstance(value, bool):
            return f"{{%bool({value})}}"
        return f"{{{json.dumps(value)}}}"

    def __init__(self):
        self.script = Script(VARIABLE_SCRIPTS)
        self.unresolvable: Set[str] = set()

    def update_script(self) -> None:
        self.script.resolve(unresolvable=self.unresolvable, update=True)

    def add(self, values: Dict[str, Any]) -> None:
        self.script.add(
            self.add_sanitized_variables(
                {name: self.to_script(value) for name, value in values.items()}
            )
        )
        self.script.resolve(unresolvable=self.unresolvable, update=True)
