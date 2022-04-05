from ytdl_subscribe.downloaders.youtube_downloader import YoutubeDownloader
from ytdl_subscribe.subscriptions.subscription import Subscription
from ytdl_subscribe.validators.config.sources.youtube_validators import (
    YoutubePlaylistDownloadValidator,
)
from ytdl_subscribe.validators.config.sources.youtube_validators import (
    YoutubeSourceValidator,
)


class YoutubeSubscription(Subscription):
    source_validator_type = YoutubeSourceValidator
    downloader_type = YoutubeDownloader

    @property
    def source_options(self) -> YoutubeSourceValidator:
        return super().source_options

    @property
    def downloader(self) -> YoutubeDownloader:
        return super().downloader


class YoutubePlaylistSubscription(YoutubeSubscription):
    download_strategy_type = YoutubePlaylistDownloadValidator

    @property
    def download_strategy_options(self) -> YoutubePlaylistDownloadValidator:
        return super().download_strategy_options

    def extract_info(self):
        entries = self.downloader.download_playlist(
            playlist_id=self.download_strategy_options.playlist_id.value
        )

        for e in entries:
            self.post_process_entry(e)
