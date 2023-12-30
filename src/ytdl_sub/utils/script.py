import json
import re
from typing import Any
from typing import Dict


class ScriptUtils:
    @classmethod
    def add_sanitized_variables(cls, variables: Dict[str, str]) -> Dict[str, str]:
        """
        Helper to add sanitized variables to a Script
        """
        sanitized_variables = {
            f"{name}_sanitized": f"{{%sanitize({name})}}" for name in variables.keys()
        }
        return dict(variables, **sanitized_variables)

    @classmethod
    def to_script(cls, value: Any) -> str:
        """
        Converts a python value to a script value
        """
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
            dumped_json = json.dumps(value, ensure_ascii=False, sort_keys=True)
            # Remove triple-single-quotes from JSON to avoid parsing issues
            dumped_json = re.sub("'{3,}", "'", dumped_json)

            out = f"{{%from_json('''{dumped_json}''')}}"

        return out
