from ytdl_subscribe.validators.base.string_datetime import StringDatetimeValidator
from ytdl_subscribe.validators.base.validators import StringValidator
from ytdl_subscribe.validators.config.source_options.mixins import DownloadDateRangeSource
from ytdl_subscribe.validators.config.source_options.source_validators import YoutubeSourceValidator


class YoutubePlaylistSourceValidator(YoutubeSourceValidator):
    _required_keys = {"playlist_id"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.playlist_id = self._validate_key("playlist_id", StringValidator)


class YoutubeVideoSourceValidator(YoutubeSourceValidator):
    _required_keys = {"video_id"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.video_id = self._validate_key("video_id", StringValidator)


class YoutubeChannelSourceValidator(YoutubeSourceValidator, DownloadDateRangeSource):
    _required_keys = {"channel_id"}
    _optional_keys = {"before", "after"}

    def __init__(self, name, value):
        YoutubeSourceValidator.__init__(self, name, value)
        DownloadDateRangeSource.__init__(self, name, value)
        self.channel_id = self._validate_key("channel_id", StringValidator)
