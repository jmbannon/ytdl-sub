from typing import Type

from tools.docgen.docgen import DocGen
from tools.docgen.entry_variables import EntryVariablesDocGen
from tools.docgen.override_variables import OverrideVariablesDocGen
from tools.docgen.plugins import PluginsDocGen
from tools.docgen.scripting_functions import ScriptingFunctionsDocGen
from ytdl_sub.utils.file_handler import get_file_md5_hash
from ytdl_sub.utils.file_handler import get_md5_hash


def _test_doc_gen(doc_gen: Type[DocGen]) -> None:
    expected_md5_hash = get_md5_hash(doc_gen.generate_and_maybe_write_to_file())
    md5_hash = get_file_md5_hash(doc_gen.LOCATION)

    if md5_hash != expected_md5_hash:
        print("generated")
        print(doc_gen.generate())

        print("expected")
        with open(doc_gen.LOCATION, "r", encoding="utf-8") as file_doc:
            print(file_doc.read())

    assert md5_hash == expected_md5_hash


class TestDocGen:
    def test_entry_variables_generated(self):
        _test_doc_gen(EntryVariablesDocGen)

    def test_override_variables_generated(self):
        _test_doc_gen(OverrideVariablesDocGen)

    def test_scripting_functions_generated(self):
        _test_doc_gen(ScriptingFunctionsDocGen)

    def test_plugins_generated(self):
        _test_doc_gen(PluginsDocGen)
