from abc import ABC
from typing import List

from ytdl_subscribe.downloaders.youtube_downloader import YoutubeDownloader
from ytdl_subscribe.entries.youtube import YoutubeVideo
from ytdl_subscribe.subscriptions.subscription import SourceT
from ytdl_subscribe.subscriptions.subscription import Subscription
from ytdl_subscribe.validators.config.config_options.config_options_validator import (
    ConfigOptionsValidator,
)
from ytdl_subscribe.validators.config.preset_validator import PresetValidator
from ytdl_subscribe.validators.config.source_options.youtube_validators import (
    YoutubeChannelSourceValidator,
)
from ytdl_subscribe.validators.config.source_options.youtube_validators import (
    YoutubePlaylistSourceValidator,
)
from ytdl_subscribe.validators.config.source_options.youtube_validators import (
    YoutubeVideoSourceValidator,
)


class YoutubeSubscription(Subscription[SourceT], ABC):
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
            entry_type=YoutubeVideo,
        )


class YoutubePlaylistSubscription(YoutubeSubscription[YoutubePlaylistSourceValidator]):
    def _extract_info(self) -> List[YoutubeVideo]:
        return self.get_downloader(YoutubeDownloader).download_playlist(
            playlist_id=self.source_options.playlist_id.value
        )


class YoutubeChannelSubscription(YoutubeSubscription[YoutubeChannelSourceValidator]):
    def _extract_info(self) -> List[YoutubeVideo]:
        source_ytdl_options = {}
        source_date_range = self.source_options.get_date_range()
        if source_date_range:
            source_ytdl_options["daterange"] = source_date_range

        downloader = self.get_downloader(YoutubeDownloader, source_ytdl_options=source_ytdl_options)
        return downloader.download_channel(channel_id=self.source_options.channel_id.value)


class YoutubeVideoSubscription(YoutubeSubscription[YoutubeVideoSourceValidator]):
    def _extract_info(self) -> List[YoutubeVideo]:
        entry = self.get_downloader(YoutubeDownloader).download_video(
            video_id=self.source_options.video_id.value
        )
        return [entry]
