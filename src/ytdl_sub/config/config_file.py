import os
from typing import Any

from ytdl_sub.config.config_validator import ConfigValidator
from ytdl_sub.config.preset import Preset
from ytdl_sub.utils.yaml import load_yaml


class ConfigFile(ConfigValidator):
    _required_keys = {"configuration", "presets"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)

        for preset_name, preset_dict in self.presets.dict.items():
            Preset.preset_partial_validate(config=self, name=preset_name, value=preset_dict)

    def initialize(self):
        """
        Configures things (umask, pgid) prior to any downloading

        Returns
        -------
        self
        """
        if self.config_options.umask:
            os.umask(int(self.config_options.umask, 8))

        return self

    @classmethod
    def from_dict(cls, config_dict: dict) -> "ConfigFile":
        """
        Parameters
        ----------
        config_dict:
            The config in dictionary format

        Returns
        -------
        Config file validator
        """
        return ConfigFile(name="", value=config_dict)

    @classmethod
    def from_file_path(cls, config_path: str) -> "ConfigFile":
        """
        Parameters
        ----------
        config_path:
            Path to the config yaml

        Returns
        -------
        Config file validator
        """
        config_dict = load_yaml(file_path=config_path)
        return ConfigFile.from_dict(config_dict)
