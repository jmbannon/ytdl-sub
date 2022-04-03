from typing import Any

from ytdl_subscribe.validators.base.validators import StringValidator
from ytdl_subscribe.validators.config.sources.source_validator import (
    DownloadStrategyValidator,
)
from ytdl_subscribe.validators.config.sources.source_validator import SourceValidator


class YoutubePlaylistDownloadValidator(DownloadStrategyValidator):
    required_fields = {"playlist_id"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.playlist_id = self.validate_key("playlist_id", StringValidator)


class YoutubeSourceValidator(SourceValidator):
    download_strategy_validator_mapping = {"playlist": YoutubePlaylistDownloadValidator}

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
