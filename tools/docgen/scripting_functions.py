import inspect
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional
from typing import Type

from tools.docgen.docgen import DocGen
from tools.docgen.utils import camel_case_to_human
from tools.docgen.utils import line_section
from tools.docgen.utils import section
from tools.docgen.utils import static_methods
from ytdl_sub.entries.script.custom_functions import CustomFunctions
from ytdl_sub.script.functions import Functions
from ytdl_sub.script.utils.type_checking import FunctionSpec


def maybe_get_function_name(function_name: str) -> Optional[str]:
    if function_name in ["register"]:
        return None

    if function_name.endswith("_"):
        return function_name[:-1]
    return function_name


def function_class_to_name(obj: Type[Any]) -> str:
    assert "Functions" in obj.__name__
    return camel_case_to_human(obj.__name__)


def function_type_hinting(display_function_name: str, function: Any) -> str:
    spec = FunctionSpec.from_callable(name=display_function_name, callable_ref=function)
    out = ":spec: ``"
    out += display_function_name
    out += spec.human_readable_input_args()
    out += " -> "
    out += spec.human_readable_output_type()
    out += "``\n\n"
    return out


def get_function_docstring(
    function_name: str, function: Any, level: int, display_function_name: Optional[str] = None
) -> str:
    display_function_name = display_function_name if display_function_name else function_name

    docs = section(display_function_name, level=level)

    docs += function_type_hinting(display_function_name=display_function_name, function=function)
    docs += inspect.cleandoc(function.__doc__)
    docs += "\n"
    return docs


class ScriptingFunctionsDocGen(DocGen):

    LOCATION = Path("docs/source/config_reference/scripting/scripting_functions.rst")

    @classmethod
    def generate(cls) -> str:
        docs = section("Scripting Functions", level=0)

        parent_objs: Dict[str, Type[Any]] = {
            function_class_to_name(obj): obj for obj in Functions.__bases__
        }
        parent_objs["Ytdl-Sub Functions"] = CustomFunctions

        for idx, name in enumerate(sorted(parent_objs.keys())):
            docs += line_section(section_idx=idx)
            docs += section(name, level=1)

            for function_name in static_methods(parent_objs[name]):
                if display_function_name := maybe_get_function_name(function_name):
                    try:
                        docs += get_function_docstring(
                            function_name=function_name,
                            display_function_name=display_function_name,
                            function=getattr(parent_objs[name], function_name),
                            level=2,
                        )
                    except Exception as exc:
                        raise ValueError(
                            f"Invalid docs for function {display_function_name}"
                        ) from exc

        return docs
