from typing import Any

import yaml

from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.base.validators import LiteralDictValidator
from ytdl_subscribe.validators.base.validators import StringValidator


class ConfigOptionsValidator(StrictDictValidator):
    """Validation for the config options"""

    _required_keys = {"working_directory"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)

        self.working_directory = self._validate_key(
            key="working_directory", validator=StringValidator
        )


class ConfigPresetsValidator(LiteralDictValidator):
    """Shallow validator checking for the presets dict in the config"""


class ConfigFileValidator(StrictDictValidator):
    _required_keys = {"configuration", "presets"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)
        self.config_options = self._validate_key(
            "configuration", ConfigOptionsValidator
        )
        self.presets = self._validate_key("presets", ConfigPresetsValidator)

    @classmethod
    def from_dict(cls, config_dict) -> "ConfigFileValidator":
        return ConfigFileValidator(name="", value=config_dict)

    @classmethod
    def from_file_path(cls, config_path) -> "ConfigFileValidator":
        # TODO: Create separate yaml file loader class
        with open(config_path, "r", encoding="utf-8") as file:
            config_dict = yaml.safe_load(file)
        return ConfigFileValidator.from_dict(config_dict)
