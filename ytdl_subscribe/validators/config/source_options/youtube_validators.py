from ytdl_subscribe.validators.base.validators import StringValidator
from ytdl_subscribe.validators.config.source_options.source_validators import YoutubeSourceValidator


class YoutubePlaylistSourceValidator(YoutubeSourceValidator):
    _required_keys = {"playlist_id"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.playlist_id = self._validate_key("playlist_id", StringValidator)
