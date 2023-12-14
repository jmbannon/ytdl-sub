from typing import Dict

from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions

v: VariableDefinitions = VARIABLES

CUSTOM_FUNCTION_SCRIPTS: Dict[str, str] = {
    "%extract_field_from_metadata_array_getter": """{
        %map_get( %map(%array_at($0, 0)), %array_at($0, 1) )
    }""",
    "%extract_field_from_metadata_array": """{
        %if(
            %bool($0),
            %array_extend(
                %array_apply(
                    %array_product(
                        %array($0),
                        [ %string($1) ]
                    ),
                    %extract_field_from_metadata_array_getter
                )
            ),
            []
        )   
    }""",
    "%extract_field_from_siblings": f"""{{
        %if(
            %bool({v.sibling_metadata.variable_name}),
            %extract_field_from_metadata_array(
                {v.sibling_metadata.variable_name},
                $0
            ),
            []
        )
    }}""",
}
