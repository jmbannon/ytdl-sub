import json
from typing import Dict

from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_scripts import VARIABLE_SCRIPTS
from ytdl_sub.script.script import Script


class TestEntry(object):
    def test_entry_to_dict(self, mock_entry, mock_entry_to_dict):
        entry_metadata: Dict[str, str] = {
            VARIABLES.entry_metadata.variable_name: f"{{{json.dumps(mock_entry._kwargs)}}}"
        }
        script = Script(dict(entry_metadata, **VARIABLE_SCRIPTS))
        output = {var_name: var_output.native for var_name, var_output in script.resolve().items()}
        del output[VARIABLES.entry_metadata.variable_name]
        del output[VARIABLES.ie_key.variable_name]
        assert output == mock_entry_to_dict
