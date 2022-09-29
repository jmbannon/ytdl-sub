from typing import List


class KwargKeys:
    keys: List[str] = []
    backend_keys: List[str] = []


def _(key: str, backend: bool = False) -> str:
    if backend:
        assert key not in KwargKeys.backend_keys
        KwargKeys.backend_keys.append(key)
    else:
        assert key not in KwargKeys.keys
        KwargKeys.keys.append(key)
    return key


SOURCE_ENTRY = _("source_entry", backend=True)
SOURCE_INDEX = _("source_index")
SOURCE_COUNT = _("source_count")
SOURCE_TITLE = _("source_title")
SOURCE_UID = _("source_uid")
SOURCE_DESCRIPTION = _("source_description")
SOURCE_WEBPAGE_URL = _("source_webpage_url")
SOURCE_UPLOADER = _("source_uploader")
SOURCE_UPLOADER_ID = _("source_uploader_id")
SOURCE_UPLOADER_URL = _("source_uploader_url")

PLAYLIST_ENTRY = _("playlist_entry", backend=True)
PLAYLIST_WEBPAGE_URL = _("playlist_webpage_url")
PLAYLIST_INDEX = _("playlist_index")
PLAYLIST_COUNT = _("playlist_count")
PLAYLIST_MAX_UPLOAD_YEAR = _("playlist_max_upload_year")
PLAYLIST_MAX_UPLOAD_YEAR_TRUNCATED = _("playlist_max_upload_year_truncated")
PLAYLIST_TITLE = _("playlist_title")
PLAYLIST_DESCRIPTION = _("playlist_description")
PLAYLIST_UID = _("playlist_uid")
PLAYLIST_UPLOADER = _("playlist_uploader")
PLAYLIST_UPLOADER_ID = _("playlist_uploader_id")
PLAYLIST_UPLOADER_URL = _("playlist_uploader_url")

UID = _("id")
EXTRACTOR = _("extractor")
EPOCH = _("epoch")
CHANNEL = _("channel")
EXT = _("ext")
TITLE = _("title")
DESCRIPTION = _("description")
WEBPAGE_URL = _("webpage_url")
UPLOADER = _("uploader")
UPLOADER_ID = _("uploader_id")
UPLOADER_URL = _("uploader_url")
