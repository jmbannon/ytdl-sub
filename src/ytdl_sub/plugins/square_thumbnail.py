from typing import List
from typing import Optional

from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.validators.options import OptionsValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.string_formatter_validators import OverridesBooleanFormatterValidator

logger = Logger.get("square-thumbnail")


class SquareThumbnailOptions(OverridesBooleanFormatterValidator, OptionsValidator):
    """
    Whether to make thumbnails square. Supports both file and embedded-based thumbnails. Ideal
    for representing audio albums.

    :Usage:

    .. code-block:: yaml

       square_thumbnail: True
    """


class SquareThumbnailPlugin(Plugin[SquareThumbnailOptions]):
    plugin_options_type = SquareThumbnailOptions

    @property
    def _square_thumbnail(self) -> bool:
        return self.overrides.evaluate_boolean(self.plugin_options)

    @classmethod
    def _convert_to_square_thumbnail(cls, entry: Entry) -> None:
        thumbnail_path = entry.get_download_thumbnail_path()
        tmp_file_path = FFMPEG.tmp_file_path(thumbnail_path)
        try:
            ffmpeg_args: List[str] = [
                "-i",
                thumbnail_path,
                "-c:v",
                "mjpeg",
                "-qmin",
                "1",
                "-qscale:v",
                "1",
                "-vf",
                "crop=min(iw\\,ih):min(iw\\,ih)",
                "-bitexact",  # for reproducibility
                tmp_file_path,
            ]
            FFMPEG.run(ffmpeg_args)
            FileHandler.move(tmp_file_path, thumbnail_path)
        finally:
            FileHandler.delete(tmp_file_path)

    def post_process_entry(self, entry: Entry) -> Optional[FileMetadata]:
        """
        Maybe make the thumbnail square
        """
        if not self._square_thumbnail:
            return None

        if not self.is_dry_run:
            if not entry.is_thumbnail_downloaded():
                logger.warning(
                    "Cannot make a square thumbnail for '%s' because it is not available",
                    entry.title,
                )
                return None

            self._convert_to_square_thumbnail(entry)

        return FileMetadata("Square thumbnail")
