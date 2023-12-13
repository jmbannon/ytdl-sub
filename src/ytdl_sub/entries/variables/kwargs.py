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
