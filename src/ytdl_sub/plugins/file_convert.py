import os
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set

from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.plugin.plugin_operation import PluginOperation
from ytdl_sub.config.validators.options import ToggleableOptionsDictValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions
from ytdl_sub.utils.exceptions import FileNotDownloadedException
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.validators.audo_codec_validator import FileTypeValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_select_validator import StringSelectValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

v: VariableDefinitions = VARIABLES


class FileConvertWithValidator(StringSelectValidator):
    _select_values = {"yt-dlp", "ffmpeg"}


class FileConvertOptions(ToggleableOptionsDictValidator):
    """
    Converts video files from one extension to another.

    :Usage:

    .. code-block:: yaml

       file_convert:
         convert_to: "mp4"

    Also supports custom ffmpeg conversions:

    :Usage:

    .. code-block:: yaml

       file_convert:
         convert_to: "mkv"
         convert_with: "ffmpeg"
         ffmpeg_post_process_args: >
           -bitexact
           -vcodec copy
           -acodec copy
           -scodec mov_text
    """

    _required_keys = {"convert_to"}
    _optional_keys = {"enable", "convert_with", "ffmpeg_post_process_args"}

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """
        Partially validate file_convert
        """
        if isinstance(value, dict):
            value["convert_to"] = value.get("convert_to", "mp3")
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)
        self._convert_to: str = self._validate_key(
            key="convert_to", validator=FileTypeValidator
        ).value
        self._convert_with: str = self._validate_key_if_present(
            key="convert_with", validator=FileConvertWithValidator, default="yt-dlp"
        ).value
        self._ffmpeg_post_process_args = self._validate_key_if_present(
            key="ffmpeg_post_process_args", validator=OverridesStringFormatterValidator
        )

        if self._convert_to == "ffmpeg" and not self._ffmpeg_post_process_args:
            raise self._validation_exception(
                "Must specify 'ffmpeg_post_process_args' if 'convert_with' is set to ffmpeg"
            )

    @property
    def convert_to(self) -> str:
        """
        :expected type: String
        :description:
          Convert to a desired file type. Supports

            - Video: avi, flv, mkv, mov, mp4, webm
            - Audio: aac, flac, mp3, m4a, opus, vorbis, wav
        """
        return self._convert_to

    @property
    def convert_with(self) -> Optional[str]:
        """
        :expected type: Optional[String]
        :description:
          Supports ``yt-dlp`` and ``ffmpeg``. ``yt-dlp`` will convert files within
          yt-dlp whereas ``ffmpeg`` specifies it will be converted using a custom command specified
          with ``ffmpeg_post_process_args``. Defaults to ``yt-dlp``.
        """
        return self._convert_with

    @property
    def ffmpeg_post_process_args(self) -> Optional[OverridesStringFormatterValidator]:
        """
        :expected type: Optional[OverridesFormatter]
        :description:
          ffmpeg args to post-process an entry file with. The args will be inserted in the
          form of

          ``ffmpeg -i input_file.ext {ffmpeg_post_process_args) output_file.output_ext``.

          The output file will use the extension specified in ``convert_to``. Post-processing args
          can still be set  with ``convert_with`` set to ``yt-dlp``.
        """
        return self._ffmpeg_post_process_args

    def modified_variables(self) -> Dict[PluginOperation, Set[str]]:
        return {PluginOperation.MODIFY_ENTRY: {v.ext.variable_name}}


class FileConvertPlugin(Plugin[FileConvertOptions]):
    plugin_options_type = FileConvertOptions

    def __init__(
        self,
        options: FileConvertOptions,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        super().__init__(
            options=options,
            overrides=overrides,
            enhanced_download_archive=enhanced_download_archive,
        )
        # Lookup of entry id to what it was converted from for logging
        self._converted_from_lookup: Dict[str, str] = {}

    def ytdl_options(self) -> Optional[Dict]:
        """
        Returns
        -------
        ffmpeg video remuxing post processing dict
        """
        if self.plugin_options.convert_with == "yt-dlp":
            return {
                "merge_output_format": self.plugin_options.convert_to,
                "postprocessors": [
                    {
                        "key": "FFmpegVideoRemuxer",
                        "when": "post_process",
                        "preferedformat": self.plugin_options.convert_to,
                    }
                ],
            }
        return None

    def modify_entry(self, entry: Entry) -> Optional[Entry]:
        """
        Parameters
        ----------
        entry
            Entry with extracted audio

        Returns
        -------
        Entry with updated 'ext' source variable

        Raises
        ------
        FileNotDownloadedException
            If the downloaded file is not found
        ValidationException
            User ffmpeg arguments errored
        """
        # Get original_ext here since there is mkv/yt-dlp shenanigans
        original_ext = entry.ext
        new_ext = self.plugin_options.convert_to

        input_video_file_path = entry.get_download_file_path()
        converted_video_file_path = entry.get_download_file_path().removesuffix(entry.ext) + new_ext

        # FFMpeg input video file should already be converted
        if self.plugin_options.convert_with == "yt-dlp":
            input_video_file_path = converted_video_file_path

        if not self.is_dry_run:
            if not os.path.isfile(input_video_file_path):
                raise FileNotDownloadedException("Failed to find the input file")

            if self.plugin_options.ffmpeg_post_process_args:
                tmp_output_file = converted_video_file_path.removesuffix(new_ext) + f"tmp.{new_ext}"
                ffmpeg_args_list = self.overrides.apply_formatter(
                    self.plugin_options.ffmpeg_post_process_args
                ).split()
                ffmpeg_args = ["-i", input_video_file_path] + ffmpeg_args_list + [tmp_output_file]
                try:
                    FFMPEG.run(ffmpeg_args)
                except Exception as exc:
                    raise ValidationException(
                        f"ffmpeg_post_process_args {' '.join(ffmpeg_args)} result in an error"
                    ) from exc

                if not os.path.isfile(tmp_output_file):
                    raise ValidationException(
                        "file_convert ffmpeg_post_process_args did not produce an output file"
                    )

                FileHandler.delete(input_video_file_path)
                FileHandler.move(tmp_output_file, converted_video_file_path)
                FileHandler.delete(tmp_output_file)

        if original_ext != new_ext:
            self._converted_from_lookup[entry.ytdl_uid()] = original_ext

        entry.add({v.ext: new_ext})

        return entry

    def post_process_entry(self, entry: Entry) -> Optional[FileMetadata]:
        """
        Add metadata about conversion if it happened
        """
        if converted_from := self._converted_from_lookup.get(entry.ytdl_uid()):
            return FileMetadata(f"Converted from {converted_from}")

        return None
