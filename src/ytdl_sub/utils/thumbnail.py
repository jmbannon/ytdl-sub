import tempfile
from urllib.request import urlopen

from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.ffmpeg import FFMPEG


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
    download_thumbnail_path = entry.get_ytdlp_download_thumbnail_path()
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
