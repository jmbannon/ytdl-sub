import inspect
from typing import Any
from typing import Dict
from typing import List
from typing import Type

LEVEL_CHARS: Dict[int, str] = {0: "=", 1: "-", 2: "~", 3: "^"}


def section(name: str, level: int) -> str:
    return f"\n{name}\n{len(name) * LEVEL_CHARS[level]}\n"


def properties(obj: Type[Any]) -> List[str]:
    return [prop for prop in dir(obj) if isinstance(getattr(obj, prop), property)]


def get_property_docs(property_name: str, obj: Any, level: int) -> str:
    docs = section(property_name, level=level)
    docs += inspect.cleandoc(getattr(obj, property_name).__doc__)
    docs += "\n"
    return docs
