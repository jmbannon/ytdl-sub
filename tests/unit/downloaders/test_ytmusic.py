from typing import Dict, Optional

import pytest

from ytdl_sub.downloaders.url.ytmusic import (
    PREFER_SONG,
    PREFER_VIDEO,
    YTMusicCounterpartResolver,
    parse_preferred_video_id,
    to_watch_url,
)

_ATV = "MUSIC_VIDEO_TYPE_ATV"
_OMV = "MUSIC_VIDEO_TYPE_OMV"


def _renderer(video_id: str, video_type: str) -> Dict:
    return {
        "videoId": video_id,
        "title": {"runs": [{"text": f"title of {video_id}"}]},
        "navigationEndpoint": {
            "watchEndpoint": {
                "watchEndpointMusicSupportedConfigs": {
                    "watchEndpointMusicConfig": {"musicVideoType": video_type}
                }
            }
        },
    }


def _response(*queue_items: Dict) -> Dict:
    return {
        "contents": {
            "singleColumnMusicWatchNextResultsRenderer": {
                "tabbedRenderer": {
                    "watchNextTabbedResultsRenderer": {
                        "tabs": [
                            {
                                "tabRenderer": {
                                    "content": {
                                        "musicQueueRenderer": {
                                            "content": {
                                                "playlistPanelRenderer": {
                                                    "contents": list(queue_items)
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    }


def _plain(video_id: str, video_type: str) -> Dict:
    return {"playlistPanelVideoRenderer": _renderer(video_id, video_type)}


def _with_switcher(primary: Dict, counterpart: Dict) -> Dict:
    return {
        "playlistPanelVideoWrapperRenderer": {
            "primaryRenderer": {"playlistPanelVideoRenderer": primary},
            "counterpart": [{"counterpartRenderer": {"playlistPanelVideoRenderer": counterpart}}],
        }
    }


class TestParsePreferredVideoId:
    def test_video_resolves_to_its_song(self):
        response = _response(
            _with_switcher(_renderer("video_id", _OMV), _renderer("song_id", _ATV))
        )
        assert parse_preferred_video_id(response, video_id="video_id", prefer=PREFER_SONG) == (
            "song_id"
        )

    def test_song_resolves_to_its_video(self):
        response = _response(
            _with_switcher(_renderer("song_id", _ATV), _renderer("video_id", _OMV))
        )
        assert parse_preferred_video_id(response, video_id="song_id", prefer=PREFER_VIDEO) == (
            "video_id"
        )

    def test_entry_already_preferred_returns_itself(self):
        response = _response(
            _with_switcher(_renderer("song_id", _ATV), _renderer("video_id", _OMV))
        )
        assert parse_preferred_video_id(response, video_id="song_id", prefer=PREFER_SONG) == (
            "song_id"
        )

    def test_no_switcher_and_already_preferred_returns_itself(self):
        response = _response(_plain("song_id", _ATV))
        assert parse_preferred_video_id(response, video_id="song_id", prefer=PREFER_SONG) == (
            "song_id"
        )

    def test_no_switcher_and_not_preferred_returns_none(self):
        response = _response(_plain("video_id", _OMV))
        assert parse_preferred_video_id(response, video_id="video_id", prefer=PREFER_SONG) is None

    @pytest.mark.parametrize(
        "response",
        [
            {},
            {"error": {"code": 400, "message": "Request contains an invalid argument."}},
            _response(),
            _response({"playlistPanelVideoRenderer": {}}),
            _response({"unexpectedRenderer": {"videoId": "video_id"}}),
        ],
        ids=["empty", "error", "no-contents", "empty-renderer", "unknown-renderer"],
    )
    def test_malformed_response_returns_none(self, response: Dict):
        assert parse_preferred_video_id(response, video_id="video_id", prefer=PREFER_SONG) is None

    def test_radio_substitution_is_rejected(self):
        """
        When the requested video is unavailable, YouTube Music serves a radio queue of
        unrelated tracks. Swapping to one of those would download the wrong song.
        """
        response = _response(
            _plain("unrelated_song_id", _ATV),
            _plain("another_song_id", _ATV),
        )
        assert (
            parse_preferred_video_id(response, video_id="unavailable_id", prefer=PREFER_SONG)
            is None
        )

    def test_radio_substitution_is_rejected_with_switcher(self):
        response = _response(
            _with_switcher(_renderer("unrelated_id", _OMV), _renderer("unrelated_song_id", _ATV))
        )
        assert parse_preferred_video_id(response, video_id="video_id", prefer=PREFER_SONG) is None


class TestResolver:
    @staticmethod
    def _resolver(response: Optional[Dict], counter: Dict) -> YTMusicCounterpartResolver:
        resolver = YTMusicCounterpartResolver(ytdl_options={})

        def _fetch_next(video_id: str) -> Optional[Dict]:
            counter["calls"] += 1
            return response

        resolver._fetch_next = _fetch_next
        return resolver

    def test_resolve_caches_per_video_and_preference(self):
        counter = {"calls": 0}
        resolver = self._resolver(
            _response(_with_switcher(_renderer("video_id", _OMV), _renderer("song_id", _ATV))),
            counter,
        )

        assert resolver.resolve(video_id="video_id", prefer=PREFER_SONG) == "song_id"
        assert resolver.resolve(video_id="video_id", prefer=PREFER_SONG) == "song_id"
        assert counter["calls"] == 1

        assert resolver.resolve(video_id="video_id", prefer=PREFER_VIDEO) == "video_id"
        assert counter["calls"] == 2

    def test_failed_fetch_resolves_to_none(self):
        counter = {"calls": 0}
        resolver = self._resolver(None, counter)

        assert resolver.resolve(video_id="video_id", prefer=PREFER_SONG) is None
        assert counter["calls"] == 1


def test_to_watch_url():
    assert to_watch_url("video_id") == "https://music.youtube.com/watch?v=video_id"
