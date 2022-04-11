from abc import ABC
from typing import List

from ytdl_subscribe.downloaders.soundcloud_downloader import SoundcloudDownloader
from ytdl_subscribe.entries.soundcloud import SoundcloudAlbum
from ytdl_subscribe.entries.soundcloud import SoundcloudTrack
from ytdl_subscribe.subscriptions.subscription import SourceT
from ytdl_subscribe.subscriptions.subscription import Subscription
from ytdl_subscribe.validators.config.config_options.config_options_validator import (
    ConfigOptionsValidator,
)
from ytdl_subscribe.validators.config.preset_validator import PresetValidator
from ytdl_subscribe.validators.config.source_options.soundcloud_validators import (
    SoundcloudAlbumsAndSinglesSourceValidator,
)


class SoundcloudSubscription(Subscription[SourceT], ABC):
    def __init__(
        self,
        name: str,
        config_options: ConfigOptionsValidator,
        preset_options: PresetValidator,
    ):
        super().__init__(
            name=name,
            config_options=config_options,
            preset_options=preset_options,
            entry_type=SoundcloudTrack,
        )


class SoundcloudAlbumsAndSinglesSubscription(
    Subscription[SoundcloudAlbumsAndSinglesSourceValidator]
):
    def _extract_info(self) -> List[SoundcloudTrack]:
        tracks: List[SoundcloudTrack] = []
        downloader = self.get_downloader(SoundcloudDownloader)

        # Get the album info first. This tells us which track ids belong
        # to an album. Unfortunately we cannot use download_archive or info.json for this
        albums: List[SoundcloudAlbum] = downloader.download_albums(
            artist_name=self.source_options.username.value
        )

        for album in albums:
            tracks += album.album_tracks(
                skip_premiere_tracks=self.source_options.skip_premiere_tracks.value
            )

        # only add tracks that are not part of an album
        single_tracks = downloader.download_tracks(artist_name=self.source_options.username.value)
        tracks += [
            track for track in single_tracks if not any(album.contains(track) for album in albums)
        ]

        return tracks
