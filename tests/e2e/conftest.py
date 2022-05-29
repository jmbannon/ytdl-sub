import tempfile

import pytest


@pytest.fixture()
def output_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir
