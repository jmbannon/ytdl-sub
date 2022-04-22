from ytdl_subscribe.plugins.music_tags import MusicTagsValidator
from ytdl_subscribe.plugins.nfo_tags import NfoTagsValidator
from ytdl_subscribe.plugins.output_directory_nfo_tags import OutputDirectoryNfoTagsValidator
from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator


class MetadataOptionsValidator(StrictDictValidator):
    _optional_keys = {"id3", "nfo", "output_directory_nfo"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self.id3 = self._validate_key_if_present(key="id3", validator=MusicTagsValidator)
        self.nfo = self._validate_key_if_present(key="nfo", validator=NfoTagsValidator)

        self.output_directory_nfo = self._validate_key_if_present(
            key="output_directory_nfo", validator=OutputDirectoryNfoTagsValidator
        )
