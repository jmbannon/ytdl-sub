import os
from typing import Any
from typing import Dict

from ytdl_sub.config.config_validator import ConfigValidator
from ytdl_sub.config.preset import Preset
from ytdl_sub.utils.exceptions import FileNotFoundException
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.yaml import load_yaml
from ytdl_sub.validators.file_path_validators import FilePathValidatorMixin


class ConfigFile(ConfigValidator):
    _required_keys = {"configuration", "presets"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)

        for preset_name, preset_dict in self.presets.dict.items():
            Preset.preset_partial_validate(config=self, name=preset_name, value=preset_dict)

        # After validation, perform initialization
        self._initialize()

    def _initialize(self):
        """
        Configures things (umask, pgid, etc) prior to any downloading

        Returns
        -------
        self
        """
        if self.config_options.umask:
            os.umask(int(self.config_options.umask, 8))

        FFMPEG.set_paths(
            ffmpeg_path=self.config_options.ffmpeg_path,
            ffprobe_path=self.config_options.ffprobe_path,
        )

        FilePathValidatorMixin.set_max_file_name_bytes(
            max_file_name_bytes=self.config_options.file_name_max_bytes
        )

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

        Raises
        ------
        FileNotFoundException
            Not found
        """
        try:
            config_dict = load_yaml(file_path=config_path)
        except FileNotFoundException as exc:
            raise FileNotFoundException(
                f"The config file '{config_path}' could not be found. "
                f"Did you set --config correctly?"
            ) from exc

        return ConfigFile.from_dict(config_dict)

    def as_dict(self) -> Dict[str, Any]:
        """
        Returns
        -------
        The config in its dict form
        """
        return self._value
