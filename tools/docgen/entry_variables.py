from tools.docgen.utils import get_property_docs
from tools.docgen.utils import properties
from tools.docgen.utils import section
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions


def generate_variable_docs() -> str:
    docs = section("Entry Variables", level=0)

    for variable_name in properties(VariableDefinitions):
        docs += get_property_docs(property_name=variable_name, obj=VariableDefinitions, level=1)

    return docs


print(generate_variable_docs())
