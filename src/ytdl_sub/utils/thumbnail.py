import logging
import os
import tempfile
from subprocess import CalledProcessError
from typing import Optional
from urllib.request import urlopen

from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.retry import retry


class ThumbnailTypes:
    LATEST_ENTRY = "latest_entry"


logger: logging.Logger = Logger.get("thumbnail")


def try_convert_download_thumbnail(entry: Entry) -> None:
    """
    Converts an entry's downloaded thumbnail into jpg format.
    Log with a warning if the thumbnail is not found or fails to convert

    Parameters
    ----------
    entry
        Entry with the thumbnail
    """
    download_thumbnail_path: Optional[str] = entry.try_get_ytdlp_download_thumbnail_path()
    download_thumbnail_path_as_jpg = entry.get_download_thumbnail_path()

    # If it was already converted, do not convert again
    if entry.is_thumbnail_downloaded():
        return

    if not download_thumbnail_path:
        logger.warning("Thumbnail for '%s' was not downloaded", entry.title)
        return

    if not download_thumbnail_path == download_thumbnail_path_as_jpg:
        try:
            FFMPEG.run(
                ["-y", "-bitexact", "-i", download_thumbnail_path, download_thumbnail_path_as_jpg]
            )
        except CalledProcessError:
            logger.warning("Failed to convert thumbnail for '%s' to jpg", entry.title)
        finally:
            FileHandler.delete(download_thumbnail_path)


@retry(times=3, exceptions=(Exception,))
def download_and_convert_url_thumbnail(
    thumbnail_url: Optional[str], output_thumbnail_path: str
) -> Optional[bool]:
    """
    Downloads and converts a thumbnail from a url into a jpg

    Parameters
    ----------
    thumbnail_url
        URL of the thumbnail
    output_thumbnail_path
        Thumbnail file destination after its converted to jpg

    Returns
    -------
    True to indicate it converted the thumbnail from url. None if the retry failed.
    """
    if not thumbnail_url:
        return None

    with urlopen(thumbnail_url, timeout=7.0) as file:
        with tempfile.NamedTemporaryFile(delete=False) as thumbnail:
            thumbnail.write(file.read())

        try:
            os.makedirs(os.path.dirname(output_thumbnail_path), exist_ok=True)

            tmp_output_path = FFMPEG.tmp_file_path(
                relative_file_path=thumbnail.name, extension="jpg"
            )
            # Add timeout of 1 second in case ffmpeg hangs from a bad thumbnail
            FFMPEG.run(["-y", "-bitexact", "-i", thumbnail.name, tmp_output_path], timeout=1)

            # Have FileHandler handle the move to a potential cross-device
            FileHandler.move(tmp_output_path, output_thumbnail_path)
        finally:
            FileHandler.delete(tmp_output_path)
            FileHandler.delete(thumbnail.name)

    return True
