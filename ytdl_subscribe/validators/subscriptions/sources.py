from typing import Any
from typing import Optional
from typing import Set

from ytdl_subscribe.validators.native.object_validator import ObjectValidator


class SubscriptionSource(ObjectValidator):
    required_fields = {"download_strategy"}
    download_strategies: Set[str] = {}

    def __init__(self, key: str, value: Any):
        super().__init__(key=key, value=value)
        self.download_strategy: Optional[str] = None

    def validate(self) -> "SubscriptionSource":
        super().validate()

        if self.value["download_strategy"] not in self.download_strategies:
            raise ValueError(
                f"'download_strategy' must be one of the following: {', '.join(self.download_strategies)}"
            )

        return self


class YoutubeSource(SubscriptionSource):
    optional_fields = {"playlist_id"}
    download_strategies = {"playlist"}

    def __init__(self, key: str, value: Any):
        super().__init__(key=key, value=value)
        self.playlist_id: Optional[str] = None

    def validate(self) -> "YoutubeSource":
        super().validate()

        if self.download_strategy == "playlist":
            self.playlist_id = self.value.get("playlist_id")
            if not self.playlist_id or not isinstance(self.playlist_id, str):
                raise ValueError(
                    "Youtube download_strategy 'playlist' requires the field 'playlist_id' to be a string"
                )

        return self


class SoundcloudSource(SubscriptionSource):
    optional_fields = {"username"}
    download_strategies = {"albums_and_singles"}

    def __init__(self, key: str, value: Any):
        super().__init__(key=key, value=value)
        self.username: Optional[str] = None

    def validate(self) -> "SoundcloudSource":
        super().validate()

        if self.download_strategy == "albums_and_singles":
            self.username = self.value.get("username")
            if not self.username or not isinstance(self.username, str):
                raise ValueError(
                    "Soundcloud download_strategy 'albums_and_singles' requires the field 'username'"
                )

        return self
