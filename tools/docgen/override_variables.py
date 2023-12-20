from tools.docgen.utils import get_function_docs
from tools.docgen.utils import section
from tools.docgen.utils import static_methods
from ytdl_sub.entries.variables.override_variables import OverrideVariables


def generate_override_docs() -> str:
    docs = section("Override Variables", level=0)

    for name in static_methods(OverrideVariables):
        docs += get_function_docs(
            function_name=name,
            obj=OverrideVariables,
            level=1,
        )

    return docs


print(generate_override_docs())
