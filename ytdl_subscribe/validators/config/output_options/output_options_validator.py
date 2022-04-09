from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.base.string_formatter_validators import (
    OverridesStringFormatterValidator,
)
from ytdl_subscribe.validators.base.string_formatter_validators import StringFormatterValidator
from ytdl_subscribe.validators.base.string_select_validator import StringSelectValidator


class ConvertThumbnailValidator(StringSelectValidator):
    """Valid image types that thumbnails can be converted to"""

    _select_values = {"jpeg"}


class OutputOptionsValidator(StrictDictValidator):
    """Where to output the final files and thumbnails"""

    _required_keys = {"output_directory", "file_name"}
    _optional_keys = {"convert_thumbnail", "thumbnail_name"}

    def __init__(self, name, value):
        super().__init__(name, value)

        # Output directory should resolve without any entry variables.
        # This is to check the directory for any download-archives before any downloads begin
        self.output_directory: OverridesStringFormatterValidator = self._validate_key(
            key="output_directory", validator=OverridesStringFormatterValidator
        )

        # file name and thumbnails however can use entry variables
        self.file_name: StringFormatterValidator = self._validate_key(
            key="file_name", validator=StringFormatterValidator
        )
        self.convert_thumbnail = self._validate_key_if_present(
            key="convert_thumbnail", validator=ConvertThumbnailValidator
        )
        self.thumbnail_name = self._validate_key_if_present(
            key="thumbnail_name", validator=StringFormatterValidator
        )
