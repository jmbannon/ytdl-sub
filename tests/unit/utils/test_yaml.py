import tempfile

import pytest

from ytdl_sub.utils.exceptions import FileNotFoundException
from ytdl_sub.utils.exceptions import InvalidYamlException
from ytdl_sub.utils.yaml import load_yaml


@pytest.fixture
def bad_yaml() -> str:
    return """
    this: 
      is:
          bad:
        asdf: 
        bad :
            :yaml
    """


@pytest.fixture
def bad_yaml_file_path(bad_yaml) -> str:
    with tempfile.NamedTemporaryFile(suffix=".yaml") as tmp_file:
        tmp_file.write(bad_yaml.encode("utf-8"))
        tmp_file.flush()
        yield tmp_file.name


def test_load_yaml_file_not_found():
    file_path = "does_not_exist.yaml"
    with pytest.raises(FileNotFoundException, match=f"The file '{file_path}' does not exist."):
        load_yaml(file_path=file_path)


def test_load_yaml_invalid_syntax(bad_yaml_file_path):
    with pytest.raises(
        InvalidYamlException,
        match=f"'{bad_yaml_file_path}' has invalid YAML, copy-paste it into a YAML checker to find the issue.",
    ):
        load_yaml(file_path=bad_yaml_file_path)
