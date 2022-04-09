from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.config.metadata_options.id3_validator import Id3Validator
from ytdl_subscribe.validators.config.metadata_options.nfo_validator import NFOValidator


class MetadataOptionsValidator(StrictDictValidator):
    _optional_keys = {"id3", "nfo", "output_directory_nfo"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self.id3 = self._validate_key_if_present(key="id3", validator=Id3Validator)
        self.nfo = self._validate_key_if_present(key="nfo", validator=NFOValidator)

        # TODO: Ensure this does not depend on entry variables, only overrides
        self.output_directory_nfo = self._validate_key_if_present(
            key="output_directory_nfo", validator=NFOValidator
        )
