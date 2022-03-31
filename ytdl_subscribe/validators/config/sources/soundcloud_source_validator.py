from typing import Any
from typing import Optional

from ytdl_subscribe.validators.config.sources.base_source_validator import (
    BaseSourceValidator,
)
from ytdl_subscribe.validators.exceptions import ValidationException


class SoundcloudSourceValidator(BaseSourceValidator):
    optional_fields = {"username", "skip_premiere_tracks"}
    download_strategies = {"albums_and_singles"}

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
        self.username: Optional[str] = None
        self.skip_premiere_tracks: Optional[bool] = None

    def validate(self) -> "SoundcloudSourceValidator":
        super().validate()

        self.skip_premiere_tracks = self.get("skip_premiere_tracks", True)
        if self.download_strategy == "albums_and_singles":
            self.username = self.value.get("username")
            if not self.username or not isinstance(self.username, str):
                raise ValidationException(
                    "Soundcloud download_strategy 'albums_and_singles' requires the field 'username'"
                )

        return self
