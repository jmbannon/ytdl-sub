import os
import tempfile
from pathlib import Path
from typing import Optional
from urllib.request import urlopen

from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.ffmpeg import FFMPEG


def _get_downloaded_thumbnail_path(entry: Entry) -> Optional[str]:
    thumbnails = entry.kwargs("thumbnails") or []
    possible_thumbnail_exts = {"jpg", "webp"}  # Always check for jpg and webp thumbs

    # The source `thumbnail` value and the actual downloaded thumbnail extension sometimes do
    # not match. Find all possible extensions by checking all available thumbnails.
    for thumbnail in thumbnails:
        possible_thumbnail_exts.add(thumbnail["url"].split(".")[-1])

    for ext in possible_thumbnail_exts:
        possible_thumbnail_path = str(Path(entry.working_directory()) / f"{entry.uid}.{ext}")
        if os.path.isfile(possible_thumbnail_path):
            return possible_thumbnail_path

    return None


def convert_download_thumbnail(entry: Entry):
    """
    Converts an entry's downloaded thumbnail into jpg format

    Parameters
    ----------
    entry
        Entry with the thumbnail

    Raises
    ------
    ValueError
        Entry thumbnail file not found
    """
    download_thumbnail_path = _get_downloaded_thumbnail_path(entry=entry)
    download_thumbnail_path_as_jpg = entry.get_download_thumbnail_path()
    if not download_thumbnail_path:
        raise ValueError("Thumbnail not found")

    if not download_thumbnail_path == download_thumbnail_path_as_jpg:
        FFMPEG.run(["-bitexact", "-i", download_thumbnail_path, download_thumbnail_path_as_jpg])


def convert_url_thumbnail(thumbnail_url: str, output_thumbnail_path: str):
    """
    Downloads and converts a thumbnail from a url into a jpg

    Parameters
    ----------
    thumbnail_url
        URL of the thumbnail
    output_thumbnail_path
        Thumbnail file destination after its converted to jpg
    """
    with urlopen(thumbnail_url) as file:
        with tempfile.NamedTemporaryFile() as thumbnail:
            thumbnail.write(file.read())

            FFMPEG.run(["-bitexact", "-i", thumbnail.name, output_thumbnail_path, "-bitexact"])
