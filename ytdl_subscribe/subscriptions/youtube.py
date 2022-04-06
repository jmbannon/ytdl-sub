from ytdl_subscribe.downloaders.youtube_downloader import YoutubeDownloader
from ytdl_subscribe.subscriptions.subscription import Subscription
from ytdl_subscribe.validators.config.source_options.youtube_validators import (
    YoutubePlaylistDownloadValidator,
)
from ytdl_subscribe.validators.config.source_options.youtube_validators import (
    YoutubeSourceValidator,
)


class YoutubePlaylistSubscription(
    Subscription[YoutubeSourceValidator, YoutubePlaylistDownloadValidator]
):
    def extract_info(self):
        entries = self.get_downloader(YoutubeDownloader).download_playlist(
            playlist_id=self.download_strategy_options.playlist_id.value
        )

        for entry in entries:
            self.post_process_entry(entry)
