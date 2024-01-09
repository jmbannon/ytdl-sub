from typing import List
from typing import Optional

import mediafile

from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.validators.options import OptionsValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.audo_codec_validator import AUDIO_CODEC_EXTS
from ytdl_sub.validators.validators import BoolValidator

logger = Logger.get("embed-thumbnail")


class EmbedThumbnailOptions(BoolValidator, OptionsValidator):
    """
    Whether to embed thumbnails to the audio/video file or not.

    :Usage:

    .. code-block:: yaml

       embed_thumbnail: True
    """


class EmbedThumbnailPlugin(Plugin[EmbedThumbnailOptions]):
    plugin_options_type = EmbedThumbnailOptions

    @property
    def _embed_thumbnail(self) -> bool:
        return self.plugin_options.value

    @classmethod
    def _embed_video_thumbnail(cls, entry: Entry) -> None:
        file_path = entry.get_download_file_path()
        thumbnail_path = entry.get_download_thumbnail_path()
        tmp_file_path = FFMPEG.tmp_file_path(file_path)
        try:
            ffmpeg_args: List[str] = [
                "-i",
                file_path,
                "-i",
                thumbnail_path,
                "-map",
                "1",
                "-map",
                "0",
                "-dn",  # ignore data streams
                "-c",
                "copy",
                "-bitexact",  # for reproducibility
                "-disposition:0",
                "attached_pic",
                tmp_file_path,
            ]
            FFMPEG.run(ffmpeg_args)
            FileHandler.move(tmp_file_path, file_path)
        finally:
            FileHandler.delete(tmp_file_path)

    @classmethod
    def _embed_audio_file(cls, entry: Entry) -> None:
        audio_file = mediafile.MediaFile(entry.get_download_file_path())
        with open(entry.get_download_thumbnail_path(), "rb") as thumb:
            mediafile_img = mediafile.Image(
                data=thumb.read(), desc="cover", type=mediafile.ImageType.front
            )

        audio_file.images = [mediafile_img]
        audio_file.save()

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
            if not entry.is_thumbnail_downloaded():
                logger.warning(
                    "Cannot embed thumbnail for '%s' because it is not available", entry.title
                )
                return None

            if entry.ext in AUDIO_CODEC_EXTS:
                self._embed_audio_file(entry)
            else:
                self._embed_video_thumbnail(entry)

        return FileMetadata("Embedded thumbnail")
