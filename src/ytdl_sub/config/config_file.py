from typing import Any

import yaml

from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.validators import LiteralDictValidator
from ytdl_sub.validators.validators import StringValidator


class ConfigOptions(StrictDictValidator):
    """Validation for global config options"""

    _required_keys = {"working_directory"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)

        self.working_directory = self._validate_key(
            key="working_directory", validator=StringValidator
        )


class ConfigFile(StrictDictValidator):
    _required_keys = {"configuration", "presets"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)
        self.config_options = self._validate_key("configuration", ConfigOptions)

        # Make sure presets is a dictionary. Will be validated in `PresetValidator`
        self.presets = self._validate_key("presets", LiteralDictValidator)

    @classmethod
    def from_dict(cls, config_dict) -> "ConfigFile":
        return ConfigFile(name="", value=config_dict)

    @classmethod
    def from_file_path(cls, config_path) -> "ConfigFile":
        # TODO: Create separate yaml file loader class
        with open(config_path, "r", encoding="utf-8") as file:
            config_dict = yaml.safe_load(file)
        return ConfigFile.from_dict(config_dict)
