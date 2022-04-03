from typing import Any

from ytdl_subscribe.validators.base.string_validator import StringValidator
from ytdl_subscribe.validators.config.sources.base_source_validator import (
    BaseSourceValidator,
)


class YoutubeSourceValidator(BaseSourceValidator):
    optional_fields = {"playlist_id"}
    download_strategies = {"playlist"}

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
        self.playlist_id = self.validate_dict_value("playlist_id", StringValidator)
