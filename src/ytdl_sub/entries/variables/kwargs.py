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


CHAPTERS = _("chapters", backend=True)
YTDL_SUB_CUSTOM_CHAPTERS = _("ytdl_sub_custom_chapters", backend=True)
SPLIT_BY_CHAPTERS_PARENT_ENTRY = _("split_by_chapters_parent_entry", backend=True)
COMMENTS = _("comments", backend=True)
UID = _("id")
EXTRACTOR = _("extractor")
EXTRACTOR_KEY = _("extractor_key")
IE_KEY = _("ie_key")
EPOCH = _("epoch")
CHANNEL = _("channel")
CHANNEL_ID = _("channel_id")
CREATOR = _("creator")
EXT = _("ext")
TITLE = _("title")
DESCRIPTION = _("description")
WEBPAGE_URL = _("webpage_url")
RELEASE_DATE = _("release_date")
UPLOAD_DATE = _("upload_date")
UPLOADER = _("uploader")
UPLOADER_ID = _("uploader_id")
UPLOADER_URL = _("uploader_url")
