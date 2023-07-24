from typing import Optional

from ytdl_sub.config.preset_options import OptionsValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.thumbnail import convert_download_thumbnail
from ytdl_sub.validators.validators import BoolValidator

logger = Logger.get("embed_thumbnail")


class EmbedThumbnailOptions(BoolValidator, OptionsValidator):
    """
    Whether to embed thumbnails to the audio/video file or not.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           embed_thumbnail: True
    """


class EmbedThumbnailPlugin(Plugin[EmbedThumbnailOptions]):
    plugin_options_type = EmbedThumbnailOptions

    @property
    def _embed_thumbnail(self) -> bool:
        return self.plugin_options.value

    def post_process_entry(self, entry: Entry) -> Optional[FileMetadata]:
        """
        Maybe embed the thumbnail
        """
        if not self._embed_thumbnail:
            return None

        if entry.ext == "webm":
            logger.warning("webm does not support embedded thumbnails, skipping")
            return None

        if not self.is_dry_run:
            # convert the entry thumbnail so it is embedded as jpg
            convert_download_thumbnail(entry=entry)

            file_path = entry.get_download_file_path()
            thumbnail_path = entry.get_download_thumbnail_path()
            tmp_file_path = FFMPEG.tmp_file_path(file_path)
            try:
                FFMPEG.run(
                    [
                        "-i",
                        file_path,
                        "-i",
                        thumbnail_path,
                        "-map",
                        "0",
                        "-map",
                        "1",
                        "-dn",  # ignore data streams
                        "-c",
                        "-copy",
                        "-c:v:1",
                        entry.thumbnail_ext,
                        "-disposition:v:1",
                        "attached_pic",
                        "-bitexact",  # for reproducibility
                        tmp_file_path,
                    ]
                )
                FileHandler.move(tmp_file_path, file_path)
            finally:
                FileHandler.delete(tmp_file_path)

        return FileMetadata("Embedded thumbnail")
