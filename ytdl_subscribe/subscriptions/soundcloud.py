from typing import List, Type

import yt_dlp as ytdl

from ytdl_subscribe import SubscriptionSource
from ytdl_subscribe.entries.soundcloud import SoundcloudAlbum, SoundcloudTrack
from ytdl_subscribe.subscriptions.subscription import Subscription


class SoundcloudSubscription(Subscription):
    source = SubscriptionSource.SOUNDCLOUD

    def extract_info(self):
        base_url = f"https://soundcloud.com/{self.options['username']}"
        tracks: List[Type[SoundcloudTrack]] = []

        if self.options.get("download_strategy") == "albums_then_tracks":
            # Get the album info first. This tells us which track ids belong
            # to an album. Unfortunately we cannot use download_archive or info.json for this
            with ytdl.YoutubeDL(self.ytdl_opts) as ytd:
                info = ytd.extract_info(base_url + "/albums")

            # For each album, parse each entry in the album
            albums = [
                SoundcloudAlbum(
                    skip_premiere_tracks=self.options["skip_premiere_tracks"], **e
                )
                for e in info["entries"]
            ]
            for album in albums:
                tracks += album.album_tracks

            with ytdl.YoutubeDL(self.ytdl_opts) as ytd:
                info = ytd.extract_info(base_url + "/tracks")

            # Skip parsing entries that have already been parsed when parsing albums
            single_tracks = [SoundcloudTrack(**e) for e in info["entries"]]
            tracks += [
                track
                for track in single_tracks
                if not any([album.contains(track) for album in albums])
            ]

            for e in tracks:
                self.post_process_entry(e)
        else:
            raise ValueError("Invalid download_strategy field for Soundcloud")
