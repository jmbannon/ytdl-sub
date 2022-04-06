from ytdl_subscribe.validators.base.validators import BoolValidator
from ytdl_subscribe.validators.base.validators import StringValidator
from ytdl_subscribe.validators.config.source_options.source_validator import (
    DownloadStrategyValidator,
)
from ytdl_subscribe.validators.config.source_options.source_validator import SourceValidator


class SoundcloudAlbumsAndSinglesDownloadValidator(DownloadStrategyValidator):
    _required_keys = {"username"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.username = self._validate_key(key="username", validator=StringValidator)


class SoundcloudSourceValidator(SourceValidator):
    _optional_keys = {"skip_premiere_tracks"}

    _download_strategy_validator_mapping = {
        "albums_and_singles": SoundcloudAlbumsAndSinglesDownloadValidator
    }

    def __init__(self, name: str, value: dict):
        super().__init__(name=name, value=value)
        self.skip_premiere_tracks = self._validate_key(
            "skip_premiere_tracks", BoolValidator, default=True
        )
