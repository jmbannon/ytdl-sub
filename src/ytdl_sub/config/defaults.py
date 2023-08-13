import os

from ytdl_sub.utils.system import IS_WINDOWS

if IS_WINDOWS:
    DEFAULT_LOCK_DIRECTORY = ""  # Not supported in Windows
    DEFAULT_FFMPEG_PATH = ".\\ffmpeg.exe"
    DEFAULT_FFPROBE_PATH = ".\\ffprobe.exe"

    MAX_FILE_NAME_BYTES = 255
else:
    DEFAULT_LOCK_DIRECTORY = "/tmp"
    DEFAULT_FFMPEG_PATH = "/usr/bin/ffmpeg"
    DEFAULT_FFPROBE_PATH = "/usr/bin/ffprobe"

    MAX_FILE_NAME_BYTES = os.pathconf("/", "PC_NAME_MAX")

# Historically was hardcoded to this value. Use this as the default
# if download_archive_path is not specified
DEFAULT_DOWNLOAD_ARCHIVE_NAME = ".ytdl-sub-{subscription_name}-download-archive.json"
