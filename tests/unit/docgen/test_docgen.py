from tools.docgen.entry_variables import EntryVariableDocGen
from ytdl_sub.utils.file_handler import get_file_md5_hash
from ytdl_sub.utils.file_handler import get_md5_hash


class TestDocGen:
    def test_entry_variables_generated(self):
        md5_hash = get_file_md5_hash(EntryVariableDocGen.LOCATION)
        expected_md5_hash = get_md5_hash(EntryVariableDocGen.generate_and_maybe_write_to_file())

        assert md5_hash == expected_md5_hash
