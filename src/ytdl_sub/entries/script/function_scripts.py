from typing import Dict

from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions

v: VariableDefinitions = VARIABLES

CUSTOM_FUNCTION_SCRIPTS: Dict[str, str] = {
    #############################################################################################
    # SIBLING GETTER
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
    #############################################################################################
    # REGEX PLUGIN
    #   $0 - input variable
    #   $1 - regex array
    #   $2 - defaults
    #   $3 - error message
    "%regex_capture_inner": """{
        %assert_then(
            %array_reduce(
                %array_apply_fixed(
                    %array_apply(
                        $1,
                        %regex_capture_groups
                    ),
                    %array_size($2),
                    %lte
                ),
                %and
            ),
            %array_overlay(
                %array(
                    %array_first(
                        %array_apply_fixed(
                            %array($1),
                            %string($0),
                            %regex_search
                        ),
                        []
                    )
                ),
                %array_extend( ['using all defaults'], $2 ),
                True
            ),
            $3
        )
    }""",
    "%regex_capture_many_required": """{
        %assert_ne(
            %regex_capture_inner(
                $0, $1, ['', '', '', '', '', '', '', '', '', ''],
                'When using %regex_capture_many, number of regex capture groups must be less than or equal to the number of defaults'
            ),
            ['using all defaults', '', '', '', '', '', '', '', '', '', ''],
            'When running %regex_capture_many_required, no regex strings were captured'
        )
    }""",
    "%regex_capture_many_with_defaults": """{
        %regex_capture_inner(
            $0, $1, $2,
            'When using %regex_capture_with_defaults, number of regex capture groups must be less than or equal to the number of defaults'
        )
    }""",
    "%regex_search_any": """{
        %ne(
            %array_at(
                %regex_capture_inner(
                    $0, $1, [],
                    'When using %regex_search_many, all regex strings must contain no capture groups'
                ),
                0
            ),
            'using all defaults'
        )
    }""",
}
