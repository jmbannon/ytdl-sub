from typing import List

from ytdl_subscribe.downloaders.soundcloud_downloader import SoundcloudDownloader
from ytdl_subscribe.entries.soundcloud import SoundcloudAlbum
from ytdl_subscribe.entries.soundcloud import SoundcloudTrack
from ytdl_subscribe.subscriptions.subscription import Subscription


class SoundcloudSubscription(Subscription):
    def extract_info(self):
        tracks: List[SoundcloudTrack] = []
        soundcloud_downloader = SoundcloudDownloader(
            output_directory=self.output_path,
            working_directory=self.WORKING_DIRECTORY,
            ytdl_options=self.ytdl_opts,
        )

        if self.options.get("download_strategy") == "albums_then_tracks":
            # Get the album info first. This tells us which track ids belong
            # to an album. Unfortunately we cannot use download_archive or info.json for this
            albums: List[SoundcloudAlbum] = soundcloud_downloader.download_albums(
                artist_name=self.options["username"]
            )

            for album in albums:
                tracks += album.album_tracks(
                    skip_premiere_tracks=self.options["skip_premiere_tracks"]
                )

            # only add tracks that are not part of an album
            single_tracks = soundcloud_downloader.download_tracks(
                artist_name=self.options["username"]
            )
            tracks += [
                track
                for track in single_tracks
                if not any(album.contains(track) for album in albums)
            ]

            for e in tracks:
                self.post_process_entry(e)
        else:
            raise ValueError("Invalid download_strategy field for Soundcloud")
