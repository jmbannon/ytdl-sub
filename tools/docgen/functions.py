from typing import Any
from typing import Dict
from typing import Optional
from typing import Type

from tools.docgen.utils import get_function_docs
from tools.docgen.utils import section
from tools.docgen.utils import static_methods
from ytdl_sub.entries.script.custom_functions import CustomFunctions
from ytdl_sub.script.functions import Functions


def maybe_get_function_name(function_name: str) -> Optional[str]:
    if function_name in ["register"]:
        return None

    if function_name.endswith("_"):
        return function_name[:-1]
    return function_name


def function_class_to_name(obj: Type[Any]) -> str:
    assert "Functions" in obj.__name__
    return obj.__name__.replace("Functions", " Functions")


def generate_function_docs() -> str:
    docs = section("Scripting Functions", level=0)

    parent_objs: Dict[str, Type[Any]] = {
        function_class_to_name(obj): obj for obj in Functions.__bases__
    }
    parent_objs["Ytdl-Sub Functions"] = CustomFunctions

    for name in sorted(parent_objs.keys()):
        docs += section(name, level=1)

        for function_name in static_methods(parent_objs[name]):
            if display_function_name := maybe_get_function_name(function_name):
                docs += get_function_docs(
                    function_name=function_name,
                    display_function_name=display_function_name,
                    obj=parent_objs[name],
                    level=2,
                )

    return docs


print(generate_function_docs())
