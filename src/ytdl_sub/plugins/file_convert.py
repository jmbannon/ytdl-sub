import os
from typing import Any
from typing import Dict
from typing import Optional

from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.variables.kwargs import EXT
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.plugins.plugin import PluginPriority
from ytdl_sub.utils.exceptions import FileNotDownloadedException
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.validators.audo_codec_validator import FileTypeValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_select_validator import StringSelectValidator


class FileConvertWithValidator(StringSelectValidator):
    _select_values = {"yt-dlp", "ffmpeg"}


class FileConvertOptions(PluginOptions):
    """
    Converts video files from one extension to another.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           file_convert:
             convert_to: "mp4"

    Supports custom ffmpeg conversions:

    .. code-block:: yaml

       presets:
         my_example_preset:
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
    _optional_keys = {"convert_with", "ffmpeg_post_process_args"}

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
        Convert to a desired file type. Supports:

        * Video: avi, flv, mkv, mov, mp4, webm
        * Audio: aac, flac, mp3, m4a, opus, vorbis, wav
        """
        return self._convert_to

    @property
    def convert_with(self) -> Optional[str]:
        """
        Optional. Supports ``yt-dlp`` and ``ffmpeg``. ``yt-dlp`` will convert files within
        yt-dlp whereas ``ffmpeg`` specifies it will be converted using a custom command specified
        with ``ffmpeg_post_process_args``. Defaults to ``yt-dlp``.

        """
        return self._convert_with

    @property
    def ffmpeg_post_process_args(self) -> Optional[OverridesStringFormatterValidator]:
        """
        Optional. ffmpeg args to post-process an entry file with. The args will be inserted in the
        form of:

        .. code-block:: bash

           ffmpeg -i input_file.ext {ffmpeg_post_process_args) output_file.output_ext

        The output file will use the extension specified in ``convert_to``. Post-processing args
        can still be set  with ``convert_with`` set to ``yt-dlp``.
        """
        return self._ffmpeg_post_process_args


class FileConvertPlugin(Plugin[FileConvertOptions]):
    plugin_options_type = FileConvertOptions
    # Perform this after regex
    priority: PluginPriority = PluginPriority(
        modify_entry=PluginPriority.MODIFY_ENTRY_AFTER_SPLIT + 1
    )

    def ytdl_options(self) -> Optional[Dict]:
        """
        Returns
        -------
        ffmpeg video remuxing post processing dict
        """
        if self.plugin_options.convert_with == "yt-dlp":
            return {
                "postprocessors": [
                    {
                        "key": "FFmpegVideoRemuxer",
                        "when": "post_process",
                        "preferedformat": self.plugin_options.convert_to,
                    }
                ]
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

                FileHandler.move(tmp_output_file, converted_video_file_path)
                FileHandler.delete(tmp_output_file)
                FileHandler.delete(input_video_file_path)

        if original_ext != new_ext:
            entry.add_kwargs(
                {
                    "__converted_from": original_ext,
                }
            )

        entry.add_kwargs({EXT: new_ext})

        return entry

    def post_process_entry(self, entry: Entry) -> Optional[FileMetadata]:
        """
        Add metadata about conversion if it happened
        """
        if converted_from := entry.kwargs_get("__converted_from"):
            return FileMetadata(f"Converted from {converted_from}")

        return None
