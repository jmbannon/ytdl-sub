import json
from typing import Any
from typing import Dict
from typing import Iterable

from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import String


class ScriptUtils:
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
        if value is None:
            out = ""
        elif isinstance(value, str):
            out = value
        elif isinstance(value, int):
            out = f"{{%int({value})}}"
        elif isinstance(value, float):
            out = f"{{%float({value})}}"
        elif isinstance(value, bool):
            out = f"{{%bool({value})}}"
        else:
            out = json.dumps(value)

        return out