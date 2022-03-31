from typing import Any
from typing import Dict
from typing import Optional

import yaml

from ytdl_subscribe.validators.config.preset import Preset
from ytdl_subscribe.validators.native.object_validator import ObjectValidator


class Config(ObjectValidator):
    required_fields = {"working_directory", "presets"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)
        self.working_directory: Optional[str] = None
        self.presets: Optional[Dict[str, Preset]] = None

    def validate(self) -> "Config":
        super().validate()

        self.working_directory = self.get("working_directory")
        self.presets = {}
        for preset_name, preset_obj in self.get("presets").items():
            self.presets[preset_name] = Preset(
                name=f"{self.name}.presets.{preset_name}", value=preset_obj
            ).validate()

        return self

    @classmethod
    def from_file_path(cls, config_path) -> "Config":
        # TODO: Create separate yaml file loader class
        with open(config_path, "r", encoding="utf-8") as file:
            config_dict = yaml.safe_load(file)

        return Config(name="config", value=config_dict).validate()
