import os
from typing import Dict
from typing import Optional

from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.variables.kwargs import EXT
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.exceptions import FileNotDownloadedException
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.validators.audo_codec_validator import FileTypeValidator


class FileConvertOptions(PluginOptions):
    """
    Converts video files from one extension to another.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           file_converter:
             convert_to: "mp4"
    """

    _required_keys = {"convert_to"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._convert_to = self._validate_key(key="convert_to", validator=FileTypeValidator).value

    @property
    def convert_to(self) -> str:
        """
        Convert to a desired file type. Supports:

        * Video: avi, flv, mkv, mov, mp4, webm
        * Audio: aac, flac, mp3, m4a, opus, vorbis, wav
        """
        return self._convert_to


class FileConvertPlugin(Plugin[FileConvertOptions]):
    plugin_options_type = FileConvertOptions

    def ytdl_options(self) -> Optional[Dict]:
        """
        Returns
        -------
        ffmpeg video remuxing post processing dict
        """
        return {
            "postprocessors": [
                {
                    "key": "FFmpegVideoRemuxer",
                    "when": "post_process",
                    "preferedformat": self.plugin_options.convert_to,
                }
            ]
        }

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
            If the audio file is not found
        """
        new_ext = self.plugin_options.convert_to
        converted_video_file = entry.get_download_file_path().removesuffix(entry.ext) + new_ext
        if not self.is_dry_run:
            if not os.path.isfile(converted_video_file):
                raise FileNotDownloadedException("Failed to find the converted video file")

        if entry.ext != new_ext:
            entry.add_kwargs(
                {
                    "__converted_from": entry.ext,
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
