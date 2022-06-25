import os
from typing import Any
from typing import Dict
from typing import Optional

from ytdl_sub.utils.yaml import load_yaml
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.validators import LiteralDictValidator
from ytdl_sub.validators.validators import StringValidator


class ConfigOptions(StrictDictValidator):
    _required_keys = {"working_directory"}
    _optional_keys = {"umask", "dl_aliases"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)

        self._working_directory = self._validate_key(
            key="working_directory", validator=StringValidator
        )
        self._umask = self._validate_key_if_present(
            key="umask", validator=StringValidator, default="022"
        )
        self._dl_aliases = self._validate_key_if_present(
            key="dl_aliases", validator=LiteralDictValidator
        )

    @property
    def working_directory(self) -> str:
        """
        The directory to temporarily store downloaded files before moving them into their final
        directory.
        """
        return self._working_directory.value

    @property
    def umask(self) -> Optional[str]:
        """
        Umask (octal format) to apply to every created file. Defaults to "022".
        """
        return self._umask.value

    @property
    def dl_aliases(self) -> Optional[Dict[str, str]]:
        """
        Alias definitions to shorten ``ytdl-sub dl`` arguments. For example,

        .. code-block:: yaml

           configuration:
             dl_aliases:
               mv: "--preset yt_music_video"
               v: "--youtube.video_url"

        Simplifies

        .. code-block:: bash

           ytdl-sub dl --preset "yt_music_video" --youtube.video_url "youtube.com/watch?v=a1b2c3"

        to

        .. code-block:: bash

           ytdl-sub dl --mv --v "youtube.com/watch?v=a1b2c3"
        """
        if self._dl_aliases:
            return self._dl_aliases.dict
        return {}


class ConfigFile(StrictDictValidator):
    _required_keys = {"configuration", "presets"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)
        self.config_options = self._validate_key("configuration", ConfigOptions)

        # Make sure presets is a dictionary. Will be validated in `PresetValidator`
        self.presets = self._validate_key("presets", LiteralDictValidator)

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
