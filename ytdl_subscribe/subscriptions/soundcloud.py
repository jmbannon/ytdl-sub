import yt_dlp as ytdl
from sanitize_filename import sanitize

from ytdl_subscribe import SubscriptionSource
from ytdl_subscribe.subscriptions.subscription import Subscription


class SoundcloudSubscription(Subscription):
    source = SubscriptionSource.SOUNDCLOUD

    def is_entry_skippable(self, entry):
        return self.options["skip_premiere_tracks"] and "/preview/" in entry["url"]

    def parse_entry(self, entry):
        entry = super(SoundcloudSubscription, self).parse_entry(entry)
        entry["upload_year"] = entry["upload_date"][:4]

        # Add thumbnail ext value
        entry["thumbnail_ext"] = entry["thumbnail"].split(".")[-1]

        # If the entry does not have album fields, set them to be the track fields
        if "album" not in entry:
            entry["album"] = entry["title"]
            entry["sanitized_album"] = entry["sanitized_title"]
            entry["album_year"] = entry["upload_year"]
            entry["tracknumber"] = 1
            entry["tracknumberpadded"] = f"{1:02d}"

        return entry

    def parse_album_entry(self, album_entry):
        album_year = min([int(e["upload_date"][:4]) for e in album_entry["entries"]])
        for track_number, e in enumerate(album_entry["entries"], start=1):
            e["album"] = album_entry["title"]
            e["sanitized_album"] = sanitize(album_entry["title"])
            e["album_year"] = album_year
            e["tracknumber"] = track_number
            e["tracknumberpadded"] = f"{track_number:02d}"
        return album_entry

    def extract_info(self):
        base_url = f"https://soundcloud.com/{self.options['username']}"
        tracks = []

        if self.options.get("download_strategy") == "albums_then_tracks":
            # Get the album info first, but do not download. This tells us which track ids belong
            # to an album. Unfortunately we cannot use download_archive or info.json for this
            with ytdl.YoutubeDL(self.ytdl_opts) as ytd:
                info = ytd.extract_info(base_url + "/albums", download=False)

            # For each album, parse each entry in the album
            album_entries = [self.parse_album_entry(a) for a in info["entries"]]
            for album_entry in album_entries:
                tracks += [
                    self.parse_entry(e)
                    for e in album_entry["entries"]
                    if not self.is_entry_skippable(e)
                ]

            # Download the tracks now, and use download_archive to cache
            track_ytdl_opts = {
                "download_archive": self.WORKING_DIRECTORY
                + "/ytdl-download-archive.txt",
            }
            with ytdl.YoutubeDL(dict(self.ytdl_opts, **track_ytdl_opts)) as ytd:
                info = ytd.extract_info(base_url + "/tracks")

            # Skip parsing entries that have already been parsed when parsing albums
            album_track_ids = [t["id"] for t in tracks]
            tracks += [
                self.parse_entry(e)
                for e in info["entries"]
                if e["id"] not in album_track_ids and not self.is_entry_skippable(e)
            ]

            for e in tracks:
                self.post_process_entry(e)
        else:
            raise ValueError("Invalid download_strategy field for Soundcloud")
