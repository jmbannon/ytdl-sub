from typing import Any
from typing import Dict
from typing import Optional

import yaml

from ytdl_subscribe.validators.base.object_validator import ObjectValidator
from ytdl_subscribe.validators.config.preset_validator import PresetValidator


class ConfigValidator(ObjectValidator):
    required_fields = {"working_directory", "presets"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)
        self.working_directory: Optional[str] = None
        self.presets: Optional[Dict[str, PresetValidator]] = None

    def validate(self) -> "ConfigValidator":
        super().validate()

        self.working_directory = self.get("working_directory")
        self.presets = {}
        for preset_name, preset_obj in self.get("presets").items():
            self.presets[preset_name] = PresetValidator(
                name=f"{self.name}.presets.{preset_name}", value=preset_obj
            ).validate()

        return self

    @classmethod
    def from_file_path(cls, config_path) -> "ConfigValidator":
        # TODO: Create separate yaml file loader class
        with open(config_path, "r", encoding="utf-8") as file:
            config_dict = yaml.safe_load(file)

        return ConfigValidator(name="config", value=config_dict).validate()
