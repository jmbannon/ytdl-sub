from typing import Optional

from ytdl_subscribe.validators.base.bool_validator import BoolValidator
from ytdl_subscribe.validators.base.string_validator import StringValidator
from ytdl_subscribe.validators.config.sources.base_source_validator import (
    BaseSourceValidator,
)


class SoundcloudSourceValidator(BaseSourceValidator):
    optional_fields = {"username", "skip_premiere_tracks"}
    download_strategies = {"albums_and_singles"}

    def __validate_and_set_download_strategy_fields(self):
        if self.download_strategy == "albums_and_singles":
            self.username = self.validate_dict_value(
                dict_value_name="username",
                validator=StringValidator,
            ).value

    def __init__(self, name: str, value: dict):
        super().__init__(name=name, value=value)
        self.skip_premiere_tracks = self.validate_dict_value(
            "skip_premiere_tracks", BoolValidator, default=True
        ).value
        self.username: Optional[str] = None
        self.__validate_and_set_download_strategy_fields()
