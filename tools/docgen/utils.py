import inspect
from functools import cached_property
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Type

from ytdl_sub.config.validators.options import OptionsValidator

LEVEL_CHARS: Dict[int, str] = {0: "=", 1: "-", 2: "~", 3: "^"}


def _should_filter_property(property_name: str) -> bool:
    return property_name.startswith("_") or property_name in (
        "value",
        "source_variable_capture_dict",
        "dict",
        "keys",
        "dict_with_format_strings",
        "subscription_name",
        "list",
        "script",
        "unresolvable",
    )


def section(name: str, level: Optional[int]) -> str:
    if level is None:
        return f"\n{name}\n\n"

    return f"\n{name}\n{len(name) * LEVEL_CHARS[level]}\n"


def properties(obj: Type[Any]) -> List[str]:
    return sorted(prop for prop in dir(obj) if isinstance(getattr(obj, prop), property))


def cached_properties(obj: Type[Any]) -> List[str]:
    return sorted(prop for prop in dir(obj) if isinstance(getattr(obj, prop), cached_property))


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


def line() -> str:
    return "\n" + ("-" * 100) + "\n"


def line_section(section_idx: int) -> str:
    if section_idx > 0:
        return line()
    return ""


def get_function_docs(
    function_name: str,
    obj: Any,
    level: Optional[int],
    display_function_name: Optional[str] = None,
    pre_docstring: Optional[str] = None,
) -> str:
    display_function_name = display_function_name if display_function_name else function_name

    docs = section(display_function_name, level=level)
    docs += pre_docstring or ""
    docs += inspect.cleandoc(getattr(obj, function_name).__doc__)
    docs += "\n"
    return docs


def generate_options_validator_docs(
    name: str, options: Type[OptionsValidator], offset: int, skip_properties: bool
) -> str:
    docs = ""
    docs += section(name, level=offset + 0)

    docs += inspect.cleandoc(options.__doc__)
    docs += "\n"

    if skip_properties:
        return docs

    property_names = [prop for prop in properties(options) if not _should_filter_property(prop)]
    for property_name in sorted(property_names):
        docs += get_function_docs(function_name=property_name, obj=options, level=None, display_function_name=f"``{property_name}``")

    return docs
