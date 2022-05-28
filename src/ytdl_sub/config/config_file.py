from typing import Any

from ytdl_sub.utils.yaml import load_yaml
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
