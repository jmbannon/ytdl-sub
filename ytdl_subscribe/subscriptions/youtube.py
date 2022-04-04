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
    download_strategy_type = YoutubePlaylistDownloadValidator

    @property
    def source_options(self) -> YoutubeSourceValidator:
        return super().source_options

    @property
    def download_strategy_options(self) -> YoutubePlaylistDownloadValidator:
        return super().download_strategy_options

    def extract_info(self):
        youtube_downloader = YoutubeDownloader(
            output_directory=self.output_options.output_directory.value,
            working_directory=self.config_options.working_directory.value,
            ytdl_options=self.ytdl_options.dict,
        )

        entries = youtube_downloader.download_playlist(
            playlist_id=self.download_strategy_options.playlist_id.value
        )

        for e in entries:
            self.post_process_entry(e)
