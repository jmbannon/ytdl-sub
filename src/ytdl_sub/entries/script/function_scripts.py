from typing import Dict

from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions

v: VariableDefinitions = VARIABLES

# TODO: Make this a proper class with docstrings
CUSTOM_FUNCTION_SCRIPTS: Dict[str, str] = {
    #############################################################################################
    # SIBLING GETTER
    "%extract_field_from_siblings": f"""{{
        %if(
            %bool({v.sibling_metadata.variable_name}),
            %array_apply_fixed(
                {v.sibling_metadata.variable_name},
                %string($0),
                %map_get
            )
            []
        )
    }}""",
}
