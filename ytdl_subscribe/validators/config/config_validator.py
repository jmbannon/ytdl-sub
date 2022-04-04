from typing import Any

import yaml

from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.base.validators import DictValidator
from ytdl_subscribe.validators.base.validators import StringValidator


class ConfigValidator(StrictDictValidator):
    _required_keys = {"working_directory", "presets"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)
        self.working_directory = self.validate_key("working_directory", StringValidator)
        self.presets = self.validate_key("presets", DictValidator)

    @classmethod
    def from_dict(cls, config_dict) -> "ConfigValidator":
        return ConfigValidator(name="config", value=config_dict)

    @classmethod
    def from_file_path(cls, config_path) -> "ConfigValidator":
        # TODO: Create separate yaml file loader class
        with open(config_path, "r", encoding="utf-8") as file:
            config_dict = yaml.safe_load(file)
        return ConfigValidator.from_dict(config_dict)
