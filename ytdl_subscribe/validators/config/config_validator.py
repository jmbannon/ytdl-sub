from typing import Any

import yaml

from ytdl_subscribe.validators.base.dict_validator import DictValidator
from ytdl_subscribe.validators.base.dict_validator import DictWithExtraFieldsValidator
from ytdl_subscribe.validators.base.string_validator import StringValidator


class ConfigValidator(DictValidator):
    required_fields = {"working_directory", "presets"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)
        self.working_directory = self.validate_dict_value(
            "working_directory", StringValidator
        )
        self.presets = self.validate_dict_value("presets", DictWithExtraFieldsValidator)

    @classmethod
    def from_file_path(cls, config_path) -> "ConfigValidator":
        # TODO: Create separate yaml file loader class
        with open(config_path, "r", encoding="utf-8") as file:
            config_dict = yaml.safe_load(file)

        return ConfigValidator(name="config", value=config_dict)
