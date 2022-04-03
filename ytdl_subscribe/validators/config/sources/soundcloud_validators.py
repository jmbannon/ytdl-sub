from ytdl_subscribe.validators.base.bool_validator import BoolValidator
from ytdl_subscribe.validators.base.string_validator import StringValidator
from ytdl_subscribe.validators.config.sources.source_validator import (
    DownloadStrategyValidator,
)
from ytdl_subscribe.validators.config.sources.source_validator import SourceValidator


class SoundcloudAlbumsAndSinglesDownloadValidator(DownloadStrategyValidator):
    required_fields = {"username"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.username = self.validate_dict_value(
            dict_value_name="username", validator=StringValidator
        ).value


class SoundcloudSourceValidator(SourceValidator):
    optional_fields = {"skip_premiere_tracks"}

    download_strategy_validator_mapping = {
        "albums_and_singles": SoundcloudAlbumsAndSinglesDownloadValidator
    }

    def __init__(self, name: str, value: dict):
        super().__init__(name=name, value=value)
        self.skip_premiere_tracks = self.validate_dict_value(
            "skip_premiere_tracks", BoolValidator, default=True
        ).value
