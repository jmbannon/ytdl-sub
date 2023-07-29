import os
import re
import tempfile

import pytest

from ytdl_sub.utils.exceptions import FileNotFoundException
from ytdl_sub.utils.exceptions import InvalidYamlException
from ytdl_sub.utils.file_handler import FileHandler
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
    # Do not delete the file in the context manager - for Windows compatibility
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp_file:
        tmp_file.write(bad_yaml.encode("utf-8"))
        tmp_file.flush()

    try:
        yield tmp_file.name
    finally:
        FileHandler.delete(tmp_file.name)


@pytest.fixture
def single_int_file_path(bad_yaml) -> str:
    # Do not delete the file in the context manager - for Windows compatibility
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp_file:
        tmp_file.write("0".encode("utf-8"))
        tmp_file.flush()

    try:
        yield tmp_file.name
    finally:
        FileHandler.delete(tmp_file.name)


@pytest.fixture
def empty_yaml_file_path(bad_yaml) -> str:
    # Do not delete the file in the context manager - for Windows compatibility
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp_file:
        pass

    try:
        yield tmp_file.name
    finally:
        FileHandler.delete(tmp_file.name)


def test_load_yaml_file_not_found():
    file_path = "does_not_exist.yaml"
    with pytest.raises(FileNotFoundException, match=f"The file '{file_path}' does not exist."):
        load_yaml(file_path=file_path)


def test_load_yaml_invalid_syntax(bad_yaml_file_path: str):
    with pytest.raises(
        InvalidYamlException,
        match=re.escape(f"'{bad_yaml_file_path}' has invalid YAML"),
    ):
        load_yaml(file_path=bad_yaml_file_path)


def test_empty_yaml(empty_yaml_file_path: str):
    with pytest.raises(
        InvalidYamlException,
        match=re.escape(f"'{empty_yaml_file_path}' was specified but does not contain any YAML."),
    ):
        load_yaml(file_path=empty_yaml_file_path)


def test_empty_yaml_only_int(single_int_file_path: str):
    with pytest.raises(
        InvalidYamlException,
        match=re.escape(f"'{single_int_file_path}' was specified but does not contain any YAML."),
    ):
        load_yaml(file_path=single_int_file_path)
