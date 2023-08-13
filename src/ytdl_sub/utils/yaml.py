import os.path
from io import StringIO
from pathlib import Path
from typing import Dict

import yaml
from yaml import YAMLError

from ytdl_sub.utils.exceptions import FileNotFoundException
from ytdl_sub.utils.exceptions import InvalidYamlException
from ytdl_sub.utils.logger import Logger

logger = Logger.get(name="yaml")


def load_yaml(file_path: str | Path) -> Dict:
    """
    Parameters
    ----------
    file_path
        Path of the file

    Returns
    -------
    Dict representation of the yaml file

    Raises
    ------
    FileNotFoundException
        The file does not exist
    InvalidYamlException
        The file has invalid yaml
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundException(f"The file '{file_path}' does not exist.")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            output = yaml.safe_load(file)
    except YAMLError as yaml_exception:
        raise InvalidYamlException(
            f"'{file_path}' has invalid YAML:\n{yaml_exception}\n\n"
            f"Copy-pasting it into a YAML parser can also help find the issue."
        ) from yaml_exception

    if not isinstance(output, dict):
        raise InvalidYamlException(f"'{file_path}' was specified but does not contain any YAML.")

    return output


def dump_yaml(to_dump: Dict) -> str:
    """
    Returns
    -------
    dict converted to YAML
    """
    string_io = StringIO()
    yaml.safe_dump(to_dump, string_io, indent=2, allow_unicode=True, sort_keys=True)
    return string_io.getvalue()
