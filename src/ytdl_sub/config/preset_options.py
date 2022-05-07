from typing import Optional

from yt_dlp.utils import sanitize_filename

from ytdl_sub.entries.entry import Entry
from ytdl_sub.validators.date_range_validator import DateRangeValidator
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import BoolValidator
from ytdl_sub.validators.validators import LiteralDictValidator


class YTDLOptions(LiteralDictValidator):
    """
    Optional. This section allows you to add any ytdl argument to ytdl-sub's downloader.
    The argument names can differ slightly from the command-line argument names. See
    `this docstring <https://github.com/yt-dlp/yt-dlp/blob/2022.04.08/yt_dlp/YoutubeDL.py#L197>`_
    for more details.

    ytdl_options should be formatted like:

    .. code-block:: yaml

           presets:
             my_example_preset:
               ytdl_options:
                 ignoreerrors: True

    where each key is a ytdl argument.
    """


# Disable for proper docstring formatting
# pylint: disable=line-too-long
class Overrides(DictFormatterValidator):
    """
    Optional. This section allows you to define variables that can be used in any string formatter.
    For example, if you want your file and thumbnail files to match without copy-pasting a large
    format string, you can define something like:

    .. code-block:: yaml

       presets:
         my_example_preset:
           overrides:
             output_directory: "/path/to/media"
             custom_file_name: "{upload_year}.{upload_month_padded}.{upload_day_padded}.{sanitized_title}"

           # Then use the override variables in the output options
           output_options:
             output_directory: "{output_directory}"
             file_name: "{custom_file_name}.{ext}"
             thumbnail_name: "{custom_file_name}.{thumbnail_ext}"

    Override variables can contain explicit values and other variables, including both override
    and source variables.
    """

    # pylint: enable=line-too-long
    def __init__(self, name, value):
        super().__init__(name, value)
        for key in self._keys:
            sanitized_key_name = f"sanitized_{key}"
            # First, sanitize the format string
            self._value[sanitized_key_name] = sanitize_filename(self._value[key].format_string)

            # Then, convert it into a StringFormatterValidator
            self._value[sanitized_key_name] = StringFormatterValidator(
                name="__should_never_fail__",
                value=self._value[sanitized_key_name],
            )

    def apply_formatter(
        self, formatter: StringFormatterValidator, entry: Optional[Entry] = None
    ) -> str:
        """
        Returns the format_string after .format has been called on it using entry (if provided) and
        override values
        """
        variable_dict = self.dict_with_format_strings
        if entry:
            variable_dict = dict(entry.to_dict(), **variable_dict)
        return formatter.apply_formatter(variable_dict)


class OutputOptions(StrictDictValidator):
    """Where to output the final files and thumbnails"""

    _required_keys = {"output_directory", "file_name"}
    _optional_keys = {
        "thumbnail_name",
        "maintain_download_archive",
        "keep_files",
    }

    def __init__(self, name, value):
        super().__init__(name, value)

        # Output directory should resolve without any entry variables.
        # This is to check the directory for any download-archives before any downloads begin
        self._output_directory: OverridesStringFormatterValidator = self._validate_key(
            key="output_directory", validator=OverridesStringFormatterValidator
        )

        # file name and thumbnails however can use entry variables
        self._file_name: StringFormatterValidator = self._validate_key(
            key="file_name", validator=StringFormatterValidator
        )
        self._thumbnail_name = self._validate_key_if_present(
            key="thumbnail_name", validator=StringFormatterValidator
        )

        self._maintain_download_archive = self._validate_key_if_present(
            key="maintain_download_archive", validator=BoolValidator, default=False
        )
        self._keep_files = self._validate_key_if_present(
            key="keep_files", validator=DateRangeValidator
        )

        if self._keep_files and not self.maintain_download_archive:
            raise self._validation_exception(
                "keep_files requires maintain_download_archive set to True"
            )

    @property
    def output_directory(self) -> OverridesStringFormatterValidator:
        """
        Required. The output directory to store all media files downloaded.
        """
        return self._output_directory

    @property
    def file_name(self) -> StringFormatterValidator:
        """
        Required. The file name for the media file. This can include directories such as
        ``"Season {upload_year}/{title}.{ext}"``, and will be placed in the output directory.
        """
        return self._file_name

    @property
    def thumbnail_name(self) -> Optional[StringFormatterValidator]:
        """
        Optional. The file name for the media's thumbnail image. This can include directories such
        as ``"Season {upload_year}/{title}.{thumbnail_ext}"``, and will be placed in the output
        directory.
        """
        return self._thumbnail_name

    @property
    def maintain_download_archive(self) -> bool:
        """
        Optional. Maintains a download archive file in the output directory for a subscription.
        It is named ``.ytdl-sub-{subscription_name}-download-archive.json``, stored in the
        output directory.

        The download archive contains a mapping of ytdl IDs to downloaded files. This is used to
        create a ytdl download-archive file when invoking a download on a subscription. This will
        prevent ytdl from redownloading media already downloaded.

        Defaults to False.
        """
        return self._maintain_download_archive.value

    @property
    def keep_files(self) -> DateRangeValidator:
        """
        Optional. Requires ``maintain_download_archive`` set to True.

        Only keeps files that are uploaded in the defined range. Should be formatted as:

        .. code-block:: yaml

           presets:
             my_example_preset:
               output_options:
                 keep_files:
                   before:
                   after:

        where ``before`` and ``after`` are date-times. A common usage of this option is to only
        fill in the after, such as:

        .. code-block:: yaml

           presets:
             my_example_preset:
               output_options:
                 keep_files:
                   after: today-2weeks

        Which translates to 'keep files uploaded in the last two weeks'.

        By default, ytdl-sub will keep all files.
        """
        return self._keep_files
