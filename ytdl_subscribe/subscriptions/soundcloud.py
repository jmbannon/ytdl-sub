from typing import List

from ytdl_subscribe.downloaders.soundcloud_downloader import SoundcloudDownloader
from ytdl_subscribe.entries.soundcloud import SoundcloudAlbum
from ytdl_subscribe.entries.soundcloud import SoundcloudTrack
from ytdl_subscribe.subscriptions.subscription import Subscription
from ytdl_subscribe.validators.config.sources.soundcloud_validators import (
    SoundcloudAlbumsAndSinglesDownloadValidator,
)
from ytdl_subscribe.validators.config.sources.soundcloud_validators import (
    SoundcloudSourceValidator,
)


class SoundcloudSubscription(Subscription):
    source_validator_type = SoundcloudSourceValidator
    downloader_type = SoundcloudDownloader

    @property
    def source_options(self) -> SoundcloudSourceValidator:
        return super().source_options

    @property
    def downloader(self) -> SoundcloudDownloader:
        return super().downloader


class SoundcloudAlbumsAndSinglesSubscription(SoundcloudSubscription):
    download_strategy_type = SoundcloudAlbumsAndSinglesDownloadValidator

    @property
    def download_strategy_options(self) -> SoundcloudAlbumsAndSinglesDownloadValidator:
        return super().download_strategy_options

    def extract_info(
        self,
    ):
        tracks: List[SoundcloudTrack] = []

        # Get the album info first. This tells us which track ids belong
        # to an album. Unfortunately we cannot use download_archive or info.json for this
        albums: List[SoundcloudAlbum] = self.downloader.download_albums(
            artist_name=self.download_strategy_options.username.value
        )

        for album in albums:
            tracks += album.album_tracks(
                skip_premiere_tracks=self.source_options.skip_premiere_tracks.value
            )

        # only add tracks that are not part of an album
        single_tracks = self.downloader.download_tracks(
            artist_name=self.download_strategy_options.username.value
        )
        tracks += [
            track
            for track in single_tracks
            if not any(album.contains(track) for album in albums)
        ]

        for e in tracks:
            self.post_process_entry(e)
