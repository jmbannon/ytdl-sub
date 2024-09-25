import os

from ytdl_sub.utils.system import IS_WINDOWS


def _existing_path(*paths: str) -> str:
    """
    Tries to search multiple paths for a file, returns a
    path if it exists. If none are valid files, returns
    the first one
    """
    for path in paths:
        if os.path.isfile(path):
            return path
    return paths[0]


if IS_WINDOWS:
    DEFAULT_LOCK_DIRECTORY = ""  # Not supported in Windows
    DEFAULT_FFMPEG_PATH = ".\\ffmpeg.exe"
    DEFAULT_FFPROBE_PATH = ".\\ffprobe.exe"

    MAX_FILE_NAME_BYTES = 255
else:
    DEFAULT_LOCK_DIRECTORY = "/tmp"
    DEFAULT_FFMPEG_PATH = os.getenv(
        "YTDL_SUB_FFMPEG_PATH", _existing_path("/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg")
    )
    DEFAULT_FFPROBE_PATH = os.getenv(
        "YTDL_SUB_FFPROBE_PATH", _existing_path("/usr/bin/ffprobe", "/usr/local/bin/ffmpeg")
    )

    MAX_FILE_NAME_BYTES = os.pathconf("/", "PC_NAME_MAX")

# Historically was hardcoded to this value. Use this as the default
# if download_archive_path is not specified
DEFAULT_DOWNLOAD_ARCHIVE_NAME = ".ytdl-sub-{subscription_name}-download-archive.json"
