from ytdl_subscribe.validators.base.validators import StringValidator
from ytdl_subscribe.validators.config.source_options.source_validators import (
    SoundcloudSourceValidator,
)


class SoundcloudAlbumsAndSinglesDownloadValidator(SoundcloudSourceValidator):
    _required_keys = {"username"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.username = self._validate_key(key="username", validator=StringValidator)
