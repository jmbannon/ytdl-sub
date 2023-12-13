import json
from typing import Any
from typing import Dict
from typing import Iterable


class ScriptUtils:
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
            out = f"{{%from_json('''{json.dumps(value, ensure_ascii=False, sort_keys=True)}''')}}"

        return out
