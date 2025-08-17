from pathlib import Path

from tools.docgen.docgen import DocGen
from tools.docgen.utils import get_function_docs
from tools.docgen.utils import section
from tools.docgen.utils import static_methods
from ytdl_sub.entries.variables.override_variables import SubscriptionVariables


class StaticVariablesDocGen(DocGen):

    LOCATION = Path("docs/source/config_reference/scripting/static_variables.rst")
    DOCSTRING_LOCATION = "src/ytdl_sub/entries/variables/override_variables.py"

    @classmethod
    def generate(cls) -> str:
        docs = section("Static Variables", level=0)

        docs += section("Subscription Variables", level=1)
        for name in static_methods(SubscriptionVariables):
            docs += get_function_docs(
                function_name=name,
                obj=SubscriptionVariables,
                level=2,
            )

        return docs
