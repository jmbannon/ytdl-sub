from abc import ABC

from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.base.validators import BoolValidator


class SourceValidator(StrictDictValidator):
    """
    Abstract class for any source validator
    """


class SoundcloudSourceValidator(SourceValidator, ABC):
    """
    Abstract source validator for all soundcloud sources.
    """

    _optional_keys = {"skip_premiere_tracks"}

    def __init__(self, name: str, value: dict):
        super().__init__(name=name, value=value)
        self.skip_premiere_tracks = self._validate_key(
            "skip_premiere_tracks", BoolValidator, default=True
        )


class YoutubeSourceValidator(SourceValidator, ABC):
    """
    Abstract source validator for all soundcloud sources.
    """
