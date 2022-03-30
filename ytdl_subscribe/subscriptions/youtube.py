import json
import os
from typing import List

import yt_dlp as ytdl

from ytdl_subscribe import SubscriptionSource
from ytdl_subscribe.entries.youtube import YoutubeVideo
from ytdl_subscribe.subscriptions.subscription import Subscription


class YoutubeSubscription(Subscription):
    source = SubscriptionSource.YOUTUBE

    def extract_info(self):
        playlist_id = self.options["playlist_id"]
        url = f"https://youtube.com/playlist?list={playlist_id}"
        track_ytdl_opts = {
            "download_archive": self.WORKING_DIRECTORY + "/ytdl-download-archive.txt",
            "writeinfojson": True,
        }

        # Do not get entries from the extract info, let it write to the info.json file and
        # load that instead. This is because if the video is already downloaded, it will
        # not fetch the metadata (maybe there is a way??)
        with ytdl.YoutubeDL(dict(self.ytdl_opts, **track_ytdl_opts)) as ytd:
            _ = ytd.extract_info(url)

        # Load the entries from info.json, ignore the playlist entry
        entries: List[YoutubeVideo] = []
        for file_name in os.listdir(self.WORKING_DIRECTORY):
            if file_name.endswith(".info.json") and not file_name.startswith(
                playlist_id
            ):
                with open(self.WORKING_DIRECTORY + "/" + file_name, "r") as f:
                    entries.append(YoutubeVideo(**json.load(f)))

        for e in entries:
            self.post_process_entry(e)
