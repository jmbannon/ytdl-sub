from abc import ABC
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from yt_dlp.utils import sanitize_filename

from ytdl_sub.entries.entry import Entry
from ytdl_sub.validators.file_path_validators import (
    OverridesStringFormatterValidatorFilePathValidator,
)
from ytdl_sub.validators.file_path_validators import StringFormatterFilePathValidator
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_datetime import StringDatetimeValidator
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import BoolValidator
from ytdl_sub.validators.validators import LiteralDictValidator


# pylint: disable=no-self-use
# pylint: disable=unused-argument
class AddsVariablesMixin(ABC):
    """
    Mixin for parts of the Preset that adds source variables
    """

    def added_source_variables(self) -> List[str]:
        """
        If the plugin adds source variables, list them here.

        Returns
        -------
        List of added source variables this plugin creates
        """
        return []

    def validate_with_variables(
        self, source_variables: List[str], override_variables: Dict[str, str]
    ) -> None:
        """
        Optional validation after init with the session's source and override variables.

        Parameters
        ----------
        source_variables
            Available source variables when running the plugin
        override_variables
            Available override variables when running the plugin
        """
        return None


# pylint: enable=no-self-use
# pylint: enable=unused-argument


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
                 # Ignore any download related errors and continue
                 ignoreerrors: True
                 # Stop downloading additional metadata/videos if it
                 # exists in your download archive
                 break_on_existing: True
                 # Stop downloading additional metadata/videos if it
                 # is out of your date range
                 break_on_reject: True
                 # Path to your YouTube cookies file to download 18+ restricted content
                 cookiefile: "/path/to/cookies/file.txt"
                 # Only download this number of videos/audio
                 max_downloads: 10
                 # Download and use English title/description/etc YouTube metadata
                 extractor_args:
                   youtube:
                     lang:
                       - "en"


    where each key is a ytdl argument. Include in the example are some popular ytdl_options.
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

    In addition, any override variable defined will automatically create a ``sanitized`` variable
    for use. In the example above, ``output_directory_sanitized`` will exist and perform
    sanitization on the value when used.
    """

    # pylint: enable=line-too-long

    def _add_override_variable(self, key_name: str, format_string: str, sanitize: bool = False):
        if sanitize:
            key_name = f"{key_name}_sanitized"
            format_string = sanitize_filename(format_string)

        self._value[key_name] = StringFormatterValidator(
            name="__should_never_fail__",
            value=format_string,
        )

    def __init__(self, name, value):
        super().__init__(name, value)

        # Add sanitized overrides
        for key in self._keys:
            self._add_override_variable(
                key_name=key,
                format_string=self._value[key].format_string,
                sanitize=True,
            )

    def apply_formatter(
        self,
        formatter: StringFormatterValidator,
        entry: Optional[Entry] = None,
        function_overrides: Dict[str, str] = None,
    ) -> str:
        """
        Parameters
        ----------
        formatter
            Formatter to apply
        entry
            Optional. Entry to add source variables to the formatter
        function_overrides
            Optional. Explicit values to override the overrides themselves and source variables

        Returns
        -------
        The format_string after .format has been called
        """
        variable_dict = self.dict_with_format_strings
        if entry:
            variable_dict = dict(entry.to_dict(), **variable_dict)
        if function_overrides:
            variable_dict = dict(variable_dict, **function_overrides)

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
             info_json_name: "{title_sanitized}.{info_json_ext}"
             maintain_download_archive: True
             keep_files_before: now
             keep_files_after: 19000101
    """

    _required_keys = {"output_directory", "file_name"}
    _optional_keys = {
        "thumbnail_name",
        "info_json_name",
        "subtitles_name",
        "maintain_download_archive",
        "keep_files_before",
        "keep_files_after",
    }

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """
        Partially validate output options
        """
        if isinstance(value, dict):
            value["output_directory"] = value.get("output_directory", "placeholder")
            value["file_name"] = value.get("file_name", "placeholder")
            # Set this to True by default in partial validate to avoid failing from keep_files
            value["maintain_download_archive"] = value.get("maintain_download_archive", True)
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)

        # Output directory should resolve without any entry variables.
        # This is to check the directory for any download-archives before any downloads begin
        self._output_directory = self._validate_key(
            key="output_directory", validator=OverridesStringFormatterValidatorFilePathValidator
        )

        # file name and thumbnails however can use entry variables
        self._file_name = self._validate_key(
            key="file_name", validator=StringFormatterFilePathValidator
        )
        self._thumbnail_name = self._validate_key_if_present(
            key="thumbnail_name", validator=StringFormatterFilePathValidator
        )
        self._info_json_name = self._validate_key_if_present(
            key="info_json_name", validator=StringFormatterFilePathValidator
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
    def info_json_name(self) -> Optional[StringFormatterValidator]:
        """
        Optional. The file name for the media's info json file. This can include directories such
        as ``"Season {upload_year}/{title}.{info_json_ext}"``, and will be placed in the output
        directory.
        """
        return self._info_json_name

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
