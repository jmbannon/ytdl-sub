import json
import time
from typing import Any, Dict, List, Optional

from yt_dlp.networking import Request

from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.retry import retry

logger = Logger.get(name="ytmusic")

# YouTube Music's InnerTube endpoint that returns the watch queue for a video
_YTM_ORIGIN = "https://music.youtube.com"
_YTM_NEXT_URL = f"{_YTM_ORIGIN}/youtubei/v1/next?alt=json"
_YTM_WATCH_URL = f"{_YTM_ORIGIN}/watch?v="

# InnerTube client name/number for YouTube Music's web player
_WEB_REMIX_CLIENT_NAME = "WEB_REMIX"
_WEB_REMIX_CLIENT_NUMBER = "67"

# The music video types YouTube Music uses. ATV is the audio-only 'song' side of the
# song/video switcher. Everything else (OMV, UGC, OFFICIAL_SOURCE_MUSIC) is a video.
_MUSIC_VIDEO_TYPE_ATV = "MUSIC_VIDEO_TYPE_ATV"

PREFER_SONG = "song"
PREFER_VIDEO = "video"
PREFER_DISABLED = "disabled"

WHEN_MISSING_ORIGINAL = "original"
WHEN_MISSING_SKIP = "skip"

# Renderer keys within the watch queue response
_PPVWR = "playlistPanelVideoWrapperRenderer"
_PPVR = "playlistPanelVideoRenderer"

# The watch queue's contents. Its first item is the requested video.
_QUEUE_CONTENTS_PATH = [
    "contents",
    "singleColumnMusicWatchNextResultsRenderer",
    "tabbedRenderer",
    "watchNextTabbedResultsRenderer",
    "tabs",
    0,
    "tabRenderer",
    "content",
    "musicQueueRenderer",
    "content",
    "playlistPanelRenderer",
    "contents",
]

_VIDEO_TYPE_PATH = [
    "navigationEndpoint",
    "watchEndpoint",
    "watchEndpointMusicSupportedConfigs",
    "watchEndpointMusicConfig",
    "musicVideoType",
]


def _nav(source: Any, path: List[Any]) -> Optional[Any]:
    """
    Traverses a nested InnerTube response using a list of dict keys and list indices.
    Returns None the moment the path does not exist.
    """
    for key in path:
        try:
            source = source[key]
        except (KeyError, IndexError, TypeError):
            return None
    return source


def _client_version() -> str:
    """
    YouTube Music derives its web client version from the current date. This is the same
    scheme ytmusicapi uses, and avoids importing yt-dlp's private ``INNERTUBE_CLIENTS``
    (the yt-dlp dependency is pinned and bumped regularly).
    """
    return "1." + time.strftime("%Y%m%d", time.gmtime()) + ".01.00"


def _next_request_body(video_id: str) -> Dict:
    """
    The ``watchEndpointMusicSupportedConfigs`` block is what makes YouTube return the
    wrapper renderer containing ``counterpart``. Without it, the queue only contains the
    plain renderer for the requested video.
    """
    return {
        "enablePersistentPlaylistPanel": True,
        "isAudioOnly": True,
        "tunerSettingValue": "AUTOMIX_SETTING_NORMAL",
        "videoId": video_id,
        "playlistId": f"RDAMVM{video_id}",
        "watchEndpointMusicSupportedConfigs": {
            "watchEndpointMusicConfig": {
                "hasPersistentPlaylistPanel": True,
                "musicVideoType": _MUSIC_VIDEO_TYPE_ATV,
            }
        },
        "context": {
            "client": {
                "clientName": _WEB_REMIX_CLIENT_NAME,
                "clientVersion": _client_version(),
            },
            "user": {},
        },
    }


def _is_song(renderer: Dict) -> bool:
    return _nav(renderer, _VIDEO_TYPE_PATH) == _MUSIC_VIDEO_TYPE_ATV


def parse_preferred_video_id(response: Dict, video_id: str, prefer: str) -> Optional[str]:
    """
    Reads the song/video switcher out of an InnerTube ``next`` response.

    Parameters
    ----------
    response
        Parsed JSON body of the ``next`` request
    video_id
        The video id that was requested, used to verify the response is actually about it
    prefer
        Either ``song`` or ``video``, denoting which side to return

    Returns
    -------
    The video id of the preferred side, which is ``video_id`` itself if it is already the
    preferred side. None if YouTube Music has no video of that type, which is the case for
    video-only releases, non-music uploads, and (when unauthenticated) most tracks.
    """
    queue_item = _nav(response, _QUEUE_CONTENTS_PATH + [0])
    if not isinstance(queue_item, dict):
        return None

    # A wrapper renderer means the song/video switcher exists for this video. Without one,
    # the queue holds a plain renderer that may or may not be the preferred side.
    if _PPVWR in queue_item:
        primary = _nav(queue_item, [_PPVWR, "primaryRenderer", _PPVR])
        counterpart = _nav(queue_item, [_PPVWR, "counterpart", 0, "counterpartRenderer", _PPVR])
    else:
        primary = queue_item.get(_PPVR)
        counterpart = None

    if not isinstance(primary, dict):
        return None

    # When the requested video is unavailable, YouTube Music silently serves a generic
    # radio queue of unrelated tracks instead. Swapping to one of those would download the
    # wrong song entirely, so only trust a response that is about the video we asked for.
    if primary.get("videoId") != video_id:
        logger.debug(
            "YouTube Music returned a queue for %s instead of %s, ignoring it",
            primary.get("videoId"),
            video_id,
        )
        return None

    for renderer in (primary, counterpart):
        if not isinstance(renderer, dict):
            continue

        if _is_song(renderer) != (prefer == PREFER_SONG):
            continue

        preferred_video_id = renderer.get("videoId")
        if isinstance(preferred_video_id, str) and preferred_video_id:
            return preferred_video_id

    return None


def to_watch_url(video_id: str) -> str:
    """
    Returns
    -------
    The YouTube Music watch URL for a video id
    """
    return f"{_YTM_WATCH_URL}{video_id}"


class YTMusicCounterpartResolver:
    """
    Resolves a YouTube Music video id to its song or video counterpart using the InnerTube
    ``next`` endpoint. The relation between the two sides of YouTube Music's song/video
    switcher is not present anywhere in yt-dlp's info json, so it must be fetched
    separately.

    Requests are made through yt-dlp's networking stack so the subscription's cookies,
    proxy and user-agent all apply. YouTube Music only exposes the switcher to signed-in
    accounts, so ``ytdl_options.cookiefile`` is effectively required.
    """

    def __init__(self, ytdl_options: Dict):
        self._ytdl_options = ytdl_options
        self._cache: Dict[str, Optional[str]] = {}
        self._is_authenticated: Optional[bool] = None
        self._warned_unauthenticated = False

    @retry(times=3, exceptions=(Exception,), wait_sec=3)
    def _fetch_next(self, video_id: str) -> Dict:
        request = Request(
            url=_YTM_NEXT_URL,
            data=json.dumps(_next_request_body(video_id)).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Origin": _YTM_ORIGIN,
                "Referer": f"{_YTM_ORIGIN}/",
                "X-YouTube-Client-Name": _WEB_REMIX_CLIENT_NUMBER,
                "X-YouTube-Client-Version": _client_version(),
            },
        )

        with YTDLP.ytdlp_downloader(self._ytdl_options) as ytdlp:
            # Authenticate using the same cookies yt-dlp downloads with. The song/video
            # switcher is only returned to signed-in accounts.
            authorization: Optional[str] = None
            try:
                youtube_ie = ytdlp.get_info_extractor("Youtube")
                # pylint: disable=protected-access
                authorization = youtube_ie._get_sid_authorization_header(origin=_YTM_ORIGIN)
                # pylint: enable=protected-access
            except Exception:  # pylint: disable=broad-except
                logger.debug("Could not build YouTube Music auth header, continuing without it")

            self._is_authenticated = bool(authorization)
            if authorization:
                request.headers["Authorization"] = authorization

            return json.loads(ytdlp.urlopen(request).read())

    def _warn_if_unauthenticated(self) -> None:
        if self._is_authenticated or self._warned_unauthenticated:
            return

        self._warned_unauthenticated = True
        logger.warning(
            "YouTube Music did not return a song/video counterpart and no YouTube cookies "
            "were provided. The song/video switcher is only exposed to signed-in accounts - "
            "set `ytdl_options.cookiefile` to use this feature."
        )

    def resolve(self, video_id: str, prefer: str) -> Optional[str]:
        """
        Parameters
        ----------
        video_id
            The video id found in the source
        prefer
            Either ``song`` or ``video``

        Returns
        -------
        The video id of the preferred side, which is ``video_id`` itself if it is already
        the preferred side. None if no video of that type exists or the lookup failed, in
        which case the caller falls back to its ``when_missing`` behavior.
        """
        cache_key = f"{prefer}:{video_id}"
        if cache_key not in self._cache:
            preferred_video_id: Optional[str] = None

            # The retry decorator returns None when every attempt failed
            if (response := self._fetch_next(video_id=video_id)) is None:
                logger.debug(
                    "Failed to fetch the YouTube Music song/video switcher for %s", video_id
                )
            else:
                preferred_video_id = parse_preferred_video_id(
                    response=response, video_id=video_id, prefer=prefer
                )

            if preferred_video_id is None:
                self._warn_if_unauthenticated()

            self._cache[cache_key] = preferred_video_id

        return self._cache[cache_key]
