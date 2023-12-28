import inspect
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

LEVEL_CHARS: Dict[int, str] = {0: "=", 1: "-", 2: "~", 3: "^"}


def section(name: str, level: int) -> str:
    return f"\n{name}\n{len(name) * LEVEL_CHARS[level]}\n"


def properties(obj: Type[Any]) -> List[str]:
    return sorted(prop for prop in dir(obj) if isinstance(getattr(obj, prop), property))


def static_methods(obj: Type[Any]) -> List[str]:
    return sorted(
        name for name in dir(obj) if isinstance(inspect.getattr_static(obj, name), staticmethod)
    )


def camel_case_to_human(string: str) -> str:
    output_str = string[0]
    for char in string[1:]:
        if char.islower():
            output_str += char
        else:
            output_str += f" {char}"

    return output_str


def get_function_docs(
    function_name: str, obj: Any, level: int, display_function_name: Optional[str] = None
) -> str:
    display_function_name = display_function_name if display_function_name else function_name

    docs = section(display_function_name, level=level)
    docs += inspect.cleandoc(getattr(obj, function_name).__doc__)
    docs += "\n"
    return docs
