from tools.docgen.docgen import REGENERATE_DOCS


def test_docgen_regenerate_disabled():
    assert REGENERATE_DOCS is False
