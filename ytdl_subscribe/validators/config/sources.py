from typing import Any
from typing import Optional
from typing import Set

from ytdl_subscribe.validators.exceptions import ValidationException
from ytdl_subscribe.validators.native.object_validator import ObjectValidator


class PresetSource(ObjectValidator):
    required_fields = {"download_strategy"}
    download_strategies: Set[str] = {}

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
        self.download_strategy: Optional[str] = None

    def validate(self) -> "PresetSource":
        super().validate()

        if self.value["download_strategy"] not in self.download_strategies:
            raise ValidationException(
                f"'download_strategy' must be one of the following: {', '.join(self.download_strategies)}"
            )

        return self


class YoutubeSource(PresetSource):
    optional_fields = {"playlist_id"}
    download_strategies = {"playlist"}

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
        self.playlist_id: Optional[str] = None

    def validate(self) -> "YoutubeSource":
        super().validate()

        if self.download_strategy == "playlist":
            self.playlist_id = self.value.get("playlist_id")
            if not self.playlist_id or not isinstance(self.playlist_id, str):
                raise ValidationException(
                    "Youtube download_strategy 'playlist' requires the field 'playlist_id' to be a string"
                )

        return self


class SoundcloudSource(PresetSource):
    optional_fields = {"username", "skip_premiere_tracks"}
    download_strategies = {"albums_and_singles"}

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
        self.username: Optional[str] = None
        self.skip_premiere_tracks: Optional[bool] = None

    def validate(self) -> "SoundcloudSource":
        super().validate()

        self.skip_premiere_tracks = self.get("skip_premiere_tracks", True)
        if self.download_strategy == "albums_and_singles":
            self.username = self.value.get("username")
            if not self.username or not isinstance(self.username, str):
                raise ValidationException(
                    "Soundcloud download_strategy 'albums_and_singles' requires the field 'username'"
                )

        return self
