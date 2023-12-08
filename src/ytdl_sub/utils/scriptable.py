import copy
import json
from abc import ABC
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Set

from ytdl_sub.entries.script.variable_scripts import UNRESOLVED_VARIABLES
from ytdl_sub.entries.script.variable_scripts import VARIABLE_SCRIPTS
from ytdl_sub.script.script import Script
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import String


class Scriptable(ABC):
    @classmethod
    def add_dummy_variables(cls, variables: Iterable[str]) -> Dict[str, Resolvable]:
        dummy_variables: Dict[str, Resolvable] = {}
        for var in variables:
            dummy_variables[var] = String("dummy_string")
            dummy_variables[f"{var}_sanitized"] = String("dummy_string")

        return dummy_variables

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
        self.script = Script(copy.deepcopy(VARIABLE_SCRIPTS))
        self.unresolvable: Set[str] = copy.deepcopy(UNRESOLVED_VARIABLES)

    def update_script(self) -> None:
        self.script.resolve(unresolvable=self.unresolvable, update=True)

    def add(self, values: Dict[str, Any]) -> None:
        self.script.add(
            self.add_sanitized_variables(
                {name: self.to_script(value) for name, value in values.items()}
            )
        )

        self.unresolvable -= set(list(values.keys()))
        self.update_script()
