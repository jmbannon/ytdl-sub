from ytdl_sub.entries.script.variable_definitions import VARIABLES


class TestEntry(object):
    def test_entry_to_dict(self, mock_entry, mock_entry_to_dict):
        output = mock_entry.script.resolve().as_native()
        del output[VARIABLES.entry_metadata.variable_name]
        del output[VARIABLES.extractor_key.variable_name]
        assert output == mock_entry_to_dict
