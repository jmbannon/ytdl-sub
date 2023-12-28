from pathlib import Path
from typing import Any
from typing import Dict
from typing import Type

from tools.docgen.docgen import DocGen
from tools.docgen.utils import camel_case_to_human, line_section
from tools.docgen.utils import get_function_docs
from tools.docgen.utils import properties
from tools.docgen.utils import section
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions


def _variable_class_to_name(obj: Type[Any]) -> str:
    assert "VariableDefinitions" in obj.__name__, f"{obj.__name__} doesnt have VariableDefinitions"
    return (
        camel_case_to_human(obj.__name__)
        .replace("Variable Definitions", "Variables")
        .replace("Ytdl Sub", "Ytdl-Sub")
    )


class EntryVariablesDocGen(DocGen):

    LOCATION = Path("docs/source/config_reference/scripting/entry_variables.rst")

    @classmethod
    def generate(cls) -> str:
        docs = section("Entry Variables", level=0)

        parent_objs: Dict[str, Type[Any]] = {
            _variable_class_to_name(obj): obj for obj in VariableDefinitions.__bases__
        }

        for idx, name in enumerate(sorted(parent_objs.keys())):
            docs += line_section(section_idx=idx)
            docs += section(name, level=1)

            for variable_function_name in properties(parent_objs[name]):
                docs += get_function_docs(
                    function_name=variable_function_name,
                    obj=parent_objs[name],
                    level=2,
                )

        return docs
