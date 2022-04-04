from typing import Optional

from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.base.string_formatter_validator import (
    StringFormatterValidator,
)
from ytdl_subscribe.validators.config.metadata_options.id3_validator import Id3Validator
from ytdl_subscribe.validators.config.metadata_options.nfo_validator import NFOValidator


class MetadataOptionsValidator(StrictDictValidator):
    optional_keys = {"id3", "nfo"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self.id3 = self.validate_key_if_present(key="id3", validator=Id3Validator)
        self.nfo = self.validate_key_if_present(key="nfo", validator=NFOValidator)

        self.output_directory: StringFormatterValidator = self.validate_key(
            key="output_directory", validator=StringFormatterValidator
        )

        self.file_name: StringFormatterValidator = self.validate_key(
            key="file_name", validator=StringFormatterValidator
        )
