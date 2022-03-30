from ytdl_subscribe.downloaders.youtube_downloader import YoutubeDownloader
from ytdl_subscribe.enums import SubscriptionSource
from ytdl_subscribe.subscriptions.subscription import Subscription


class YoutubeSubscription(Subscription):
    source = SubscriptionSource.YOUTUBE

    def extract_info(self):
        youtube_downloader = YoutubeDownloader(
            output_directory=self.output_path,
            working_directory=self.WORKING_DIRECTORY,
            ytdl_options=self.ytdl_opts,
        )

        entries = youtube_downloader.download_playlist(
            playlist_id=self.options["playlist_id"]
        )

        for e in entries:
            self.post_process_entry(e)
