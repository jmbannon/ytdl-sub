from pathlib import Path

from tools.docgen.docgen import DocGen
from tools.docgen.utils import get_function_docs
from tools.docgen.utils import section
from tools.docgen.utils import static_methods
from ytdl_sub.entries.variables.override_variables import OverrideVariables


class OverrideVariablesDocGen(DocGen):

    LOCATION = Path("docs/source/config_reference/scripting/override_variables.rst")

    @classmethod
    def generate(cls) -> str:
        docs = section("Override Variables", level=0)

        for name in static_methods(OverrideVariables):
            docs += get_function_docs(
                function_name=name,
                obj=OverrideVariables,
                level=1,
            )

        return docs
