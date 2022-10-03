from typing import Dict
from typing import Optional

from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.plugins.plugin import PluginPriority
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.validators.validators import LiteralDictValidator


class FileConvertOptions(PluginOptions):
    """
    Converts media files from one extension to another.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           file_converter:
             convert:
               webm: "mp4"
    """

    _required_keys = {"convert"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._convert = self._validate_key(key="convert", validator=LiteralDictValidator).dict

    @property
    def convert(self) -> Dict[str, str]:
        """
        Convert from one extension to another
        """
        return self._convert


class FileConvertPlugin(Plugin[FileConvertOptions]):
    plugin_options_type = FileConvertOptions
    priority = PluginPriority(modify_entry=0)

    def modify_entry(self, entry: Entry) -> Entry:
        """
        If the entry is of the specified file type, convert it
        """
        for convert_from, convert_to in self.plugin_options.convert.items():
            # Entry ext does not need conversion
            if entry.ext != convert_from:
                continue

            # Entry ext needs conversion
            input_file_path = entry.get_download_file_path()
            output_file_path = input_file_path.removesuffix(entry.ext) + convert_to

            ffmpeg_args = ["-bitexact", "-i", input_file_path, "-c", "copy", output_file_path]

            if not self.is_dry_run:
                FFMPEG.run(ffmpeg_args)
                FileHandler.delete(input_file_path)

            entry.add_kwargs(
                {
                    "ext": convert_to,
                    "__converted_from": convert_from,
                }
            )

            return entry

        return entry

    def post_process_entry(self, entry: Entry) -> Optional[FileMetadata]:
        """
        Add metadata about conversion if it happened
        """
        if converted_from := entry.kwargs_get("__converted_from"):
            return FileMetadata(f"Converted from {converted_from}")

        return None
