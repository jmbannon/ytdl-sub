from typing import Any
from typing import Optional

from ytdl_subscribe.validators.config.sources.base_source_validator import (
    BaseSourceValidator,
)
from ytdl_subscribe.validators.exceptions import ValidationException


class YoutubeSourceValidator(BaseSourceValidator):
    optional_fields = {"playlist_id"}
    download_strategies = {"playlist"}

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
        self.playlist_id: Optional[str] = None

    def validate(self) -> "YoutubeSourceValidator":
        super().validate()

        if self.download_strategy == "playlist":
            self.playlist_id = self.value.get("playlist_id")
            if not self.playlist_id or not isinstance(self.playlist_id, str):
                raise ValidationException(
                    "Youtube download_strategy 'playlist' requires the field 'playlist_id' to be a string"
                )

        return self
