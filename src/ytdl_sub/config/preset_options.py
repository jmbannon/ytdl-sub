from typing import List
from typing import Optional

from yt_dlp.utils import DateRange
from yt_dlp.utils import sanitize_filename

from ytdl_sub.entries.entry import Entry
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_datetime import StringDatetimeValidator
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.string_select_validator import StringSelectValidator
from ytdl_sub.validators.validators import BoolValidator
from ytdl_sub.validators.validators import LiteralDictValidator
from ytdl_sub.validators.validators import StringListValidator


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
             custom_file_name: "{upload_year}.{upload_month_padded}.{upload_day_padded}.{title_sanitized}"

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
            key_name_sanitized = f"{key}_sanitized"
            # First, sanitize the format string
            self._value[key_name_sanitized] = sanitize_filename(self._value[key].format_string)

            # Then, convert it into a StringFormatterValidator
            self._value[key_name_sanitized] = StringFormatterValidator(
                name="__should_never_fail__",
                value=self._value[key_name_sanitized],
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
    """
    Defines where to output files and thumbnails after all post-processing has completed.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           output_options:
             # required
             output_directory: "/path/to/videos_or_music"
             file_name: "{title_sanitized}.{ext}"
             # optional
             thumbnail_name: "{title_sanitized}.{thumbnail_ext}"
             maintain_download_archive: True
             keep_files_before: now
             keep_files_after: 19000101
    """

    _required_keys = {"output_directory", "file_name"}
    _optional_keys = {
        "thumbnail_name",
        "subtitles_name",
        "maintain_download_archive",
        "keep_files_before",
        "keep_files_after",
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

        self._keep_files_before = self._validate_key_if_present(
            "keep_files_before", StringDatetimeValidator
        )
        self._keep_files_after = self._validate_key_if_present(
            "keep_files_after", StringDatetimeValidator
        )

        if (
            self._keep_files_before or self._keep_files_after
        ) and not self.maintain_download_archive:
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
    def keep_files_before(self) -> Optional[StringDatetimeValidator]:
        """
        Optional. Requires ``maintain_download_archive`` set to True.

        Only keeps files that are uploaded before this datetime. By default, ytdl-sub will keep
        files before ``now``, which implies all files.
        """
        return self._keep_files_before

    @property
    def keep_files_after(self) -> Optional[StringDatetimeValidator]:
        """
        Optional. Requires ``maintain_download_archive`` set to True.

        Only keeps files that are uploaded after this datetime. By default, ytdl-sub will keep
        files after ``19000101``, which implies all files.
        """
        return self._keep_files_after

    def get_upload_date_range_to_keep(self) -> Optional[DateRange]:
        """
        Returns
        -------
        Date range if the 'before' or 'after' is defined. None otherwise.
        """
        if self.keep_files_before or self.keep_files_after:
            return DateRange(
                start=self.keep_files_after.datetime_str if self.keep_files_after else None,
                end=self.keep_files_before.datetime_str if self.keep_files_before else None,
            )
        return None


class SubtitlesTypeValidator(StringSelectValidator):
    _expected_value_type_name = "subtitles type"
    _select_values = {"srt", "vtt", "ass", "lrc"}


class SubtitleOptions(StrictDictValidator):
    _optional_keys = {
        "subtitles_name",
        "subtitles_type",
        "embed_subtitles",
        "languages",
        "allow_auto_generated_subtitles",
    }

    def __init__(self, name, value):
        super().__init__(name, value)
        self._subtitles_name = self._validate_key_if_present(
            key="subtitles_name", validator=StringFormatterValidator
        )
        self._subtitles_type = self._validate_key_if_present(
            key="subtitles_type", validator=SubtitlesTypeValidator, default="srt"
        )
        self._embed_subtitles = self._validate_key_if_present(
            key="embed_subtitles", validator=BoolValidator
        )
        self._languages = self._validate_key_if_present(
            key="languages", validator=StringListValidator, default=["en"]
        ).list
        self._allow_auto_generated_subtitles = self._validate_key_if_present(
            key="allow_auto_generated_subtitles", validator=BoolValidator, default=False
        ).value

    @property
    def subtitles_name(self) -> Optional[StringFormatterValidator]:
        """
        Optional. The file name for the media's subtitles if they are present. This can include
        directories such as ``"Season {upload_year}/{title}.{subtitle_ext}"``, and will be placed
        in the output directory.
        """
        return self._subtitles_name

    @property
    def subtitles_type(self) -> Optional[str]:
        """
        Optional. The subtitles file format. Defaults to ``srt``
        """
        return self._subtitles_type

    @property
    def embed_subtitles(self) -> Optional[bool]:
        """
        Optional. Whether to embed the subtitles into the video file.
        """
        return self._subtitles_type

    @property
    def languages(self) -> Optional[List[str]]:
        """
        Optional. Language(s) to download for subtitles. Defaults to ``en``
        """
        return [lang.value for lang in self._languages]

    @property
    def allow_auto_generated_subtitles(self) -> Optional[bool]:
        """
        Optional. Whether to allow auto generated subtitles. Defaults to False.
        """
        return self._allow_auto_generated_subtitles
