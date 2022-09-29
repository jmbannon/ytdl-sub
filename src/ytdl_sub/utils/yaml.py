import os.path
from pathlib import Path
from typing import Dict

import yaml
from yaml import YAMLError

from ytdl_sub.utils.exceptions import FileNotFoundException
from ytdl_sub.utils.exceptions import InvalidYamlException


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
            return yaml.safe_load(file)
    except YAMLError as yaml_exception:
        raise InvalidYamlException(
            f"'{file_path}' has invalid YAML, copy-paste it into a YAML checker to find the issue."
        ) from yaml_exception
