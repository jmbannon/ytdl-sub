from typing import Any
from typing import Dict
from typing import Optional

from ytdl_sub.config.defaults import DEFAULT_DOWNLOAD_ARCHIVE_NAME
from ytdl_sub.config.overrides import Overrides
from ytdl_sub.validators.file_path_validators import OverridesStringFormatterFilePathValidator
from ytdl_sub.validators.file_path_validators import StringFormatterFileNameValidator
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_datetime import StringDatetimeValidator
from ytdl_sub.validators.string_formatter_validators import OverridesIntegerFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import (
    UnstructuredOverridesDictFormatterValidator,
)
from ytdl_sub.validators.validators import BoolValidator


class YTDLOptions(UnstructuredOverridesDictFormatterValidator):
    """
    Allows you to add any ytdl argument to ytdl-sub's downloader.
    The argument names can differ slightly from the command-line argument names. See
    `this docstring <https://github.com/yt-dlp/yt-dlp/blob/2022.04.08/yt_dlp/YoutubeDL.py#L197>`_
    for more details.

    :Usage:

    .. code-block:: yaml

           presets:
             my_example_preset:
               ytdl_options:
                 # Ignore any download related errors and continue
                 ignoreerrors: True
                 # Stop downloading additional metadata/videos if it
                 # exists in your download archive
                 break_on_existing: True
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

    def to_native_dict(self, overrides: Overrides) -> Dict:
        """
        Materializes the entire ytdl-options dict from OverrideStringFormatters into
        native python
        """
        return {
            key: overrides.apply_overrides_formatter_to_native(val)
            for key, val in self.dict.items()
        }


# Disable for proper docstring formatting
# pylint: disable=line-too-long


class OutputOptions(StrictDictValidator):
    """
    Defines where to output files and thumbnails after all post-processing has completed.

    :Usage:

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
             download_archive_name: ".ytdl-sub-{subscription_name}-download-archive.json"
             migrated_download_archive_name: ".ytdl-sub-{subscription_name_sanitized}-download-archive.json"
             maintain_download_archive: True
             keep_files_before: now
             keep_files_after: 19000101
    """

    _required_keys = {"output_directory", "file_name"}
    _optional_keys = {
        "thumbnail_name",
        "info_json_name",
        "download_archive_name",
        "migrated_download_archive_name",
        "maintain_download_archive",
        "keep_files_before",
        "keep_files_after",
        "keep_max_files",
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
            key="output_directory", validator=OverridesStringFormatterFilePathValidator
        )

        # file name and thumbnails however can use entry variables
        self._file_name = self._validate_key(
            key="file_name", validator=StringFormatterFileNameValidator
        )
        self._thumbnail_name = self._validate_key_if_present(
            key="thumbnail_name", validator=StringFormatterFileNameValidator
        )
        self._info_json_name = self._validate_key_if_present(
            key="info_json_name", validator=StringFormatterFileNameValidator
        )

        self._download_archive_name = self._validate_key_if_present(
            key="download_archive_name",
            validator=OverridesStringFormatterValidator,
            default=DEFAULT_DOWNLOAD_ARCHIVE_NAME,
        )
        self._migrated_download_archive_name = self._validate_key_if_present(
            key="migrated_download_archive_name",
            validator=OverridesStringFormatterValidator,
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
        self._keep_max_files = self._validate_key_if_present(
            "keep_max_files", OverridesIntegerFormatterValidator
        )

        if (
            self._keep_files_before or self._keep_files_after or self._keep_max_files
        ) and not self.maintain_download_archive:
            raise self._validation_exception(
                "keep_files/keep_max requires maintain_download_archive set to True"
            )

    @property
    def output_directory(self) -> OverridesStringFormatterValidator:
        """
        :expected type: OverridesFormatter
        :description:
          The output directory to store all media files downloaded.
        """
        return self._output_directory

    @property
    def file_name(self) -> StringFormatterValidator:
        """
        :expected type: EntryFormatter
        :description:
          The file name for the media file. This can include directories such as
          ``"Season {upload_year}/{title}.{ext}"``, and will be placed in the output directory.
        """
        return self._file_name

    @property
    def thumbnail_name(self) -> Optional[StringFormatterValidator]:
        """
        :expected type: Optional[EntryFormatter]
        :description:
          The file name for the media's thumbnail image. This can include directories such
          as ``"Season {upload_year}/{title}.{thumbnail_ext}"``, and will be placed in the output
          directory. Can be set to empty string or `null` to disable thumbnail writes.
        """
        return self._thumbnail_name

    @property
    def info_json_name(self) -> Optional[StringFormatterValidator]:
        """
        :expected type: Optional[EntryFormatter]
        :description:
          The file name for the media's info json file. This can include directories such
          as ``"Season {upload_year}/{title}.{info_json_ext}"``, and will be placed in the output
          directory. Can be set to empty string or `null` to disable info json writes.
        """
        return self._info_json_name

    @property
    def download_archive_name(self) -> Optional[OverridesStringFormatterValidator]:
        """
        :expected type: Optional[OverridesFormatter]
        :description:
          The file name to store a subscriptions download archive placed relative to
          the output directory. Defaults to ``.ytdl-sub-{subscription_name}-download-archive.json``
        """
        return self._download_archive_name

    @property
    def migrated_download_archive_name(self) -> Optional[OverridesStringFormatterValidator]:
        """
        :expected type: Optional[OverridesFormatter]
        :description:
          Intended to be used if you are migrating a subscription with either a new
          subscription name or output directory. It will try to load the archive file using this
          name first, and fallback to ``download_archive_name``. It will always save to this file
          and remove the original ``download_archive_name``.
        """
        return self._migrated_download_archive_name

    @property
    def maintain_download_archive(self) -> bool:
        """
        :expected type: Optional[Boolean]
        :description:
          Maintains a download archive file in the output directory for a subscription.
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
        :expected type: Optional[OverridesFormatter]
        :description:
          Requires ``maintain_download_archive`` set to True. Uses the same syntax as the
          ``date_range`` plugin.

          Only keeps files that are uploaded before this datetime. By default, ytdl-sub will keep
          files before ``now``, which implies all files. Can be used in conjunction with
          ``keep_max_files``.
        """
        return self._keep_files_before

    @property
    def keep_files_after(self) -> Optional[StringDatetimeValidator]:
        """
        :expected type: Optional[OverridesFormatter]
        :description:
          Requires ``maintain_download_archive`` set to True. Uses the same syntax as the
          ``date_range`` plugin.

          Only keeps files that are uploaded after this datetime. By default, ytdl-sub will keep
          files after ``19000101``, which implies all files. Can be used in conjunction with
          ``keep_max_files``.
        """
        return self._keep_files_after

    @property
    def keep_max_files(self) -> Optional[OverridesIntegerFormatterValidator]:
        """
        :expected type: Optional[OverridesFormatter]
        :description:
          Requires ``maintain_download_archive`` set to True.

          Only keeps N most recently uploaded videos. If set to <= 0, ``keep_max_files`` will not be
          applied. Can be used in conjunction with ``keep_files_before`` and ``keep_files_after``.
        """
        return self._keep_max_files
