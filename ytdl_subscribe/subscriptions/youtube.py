from typing import List

from ytdl_subscribe.downloaders.youtube_downloader import YoutubeDownloader
from ytdl_subscribe.entries.youtube import YoutubeVideo
from ytdl_subscribe.subscriptions.subscription import Subscription
from ytdl_subscribe.validators.config.source_options.youtube_validators import (
    YoutubeChannelSourceValidator,
)
from ytdl_subscribe.validators.config.source_options.youtube_validators import (
    YoutubePlaylistSourceValidator,
)
from ytdl_subscribe.validators.config.source_options.youtube_validators import (
    YoutubeVideoSourceValidator,
)


class YoutubePlaylistSubscription(Subscription[YoutubePlaylistSourceValidator, YoutubeVideo]):
    """
    Youtube subscription to download videos from a playlist
    """

    def _extract_info(self) -> List[YoutubeVideo]:
        return self.get_downloader(YoutubeDownloader).download_playlist(
            playlist_id=self.source_options.playlist_id.value
        )


class YoutubeChannelSubscription(Subscription[YoutubeChannelSourceValidator, YoutubeVideo]):
    """
    Youtube subscription to download videos from a channel
    """

    def _extract_info(self) -> List[YoutubeVideo]:
        source_ytdl_options = {}
        source_date_range = self.source_options.get_date_range()
        if source_date_range:
            source_ytdl_options["daterange"] = source_date_range

        downloader = self.get_downloader(YoutubeDownloader, source_ytdl_options=source_ytdl_options)
        return downloader.download_channel(channel_id=self.source_options.channel_id.value)


class YoutubeVideoSubscription(Subscription[YoutubeVideoSourceValidator, YoutubeVideo]):
    """
    Youtube subscription to download a single video
    """

    def _extract_info(self) -> List[YoutubeVideo]:
        entry = self.get_downloader(YoutubeDownloader).download_video(
            video_id=self.source_options.video_id.value
        )
        return [entry]
