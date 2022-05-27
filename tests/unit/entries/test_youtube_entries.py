import pytest

from ytdl_sub.entries.soundcloud import SoundcloudTrack
from ytdl_sub.entries.youtube import YoutubeVideo


@pytest.fixture
def playlist_index():
    return 1


@pytest.fixture
def playlist_size():
    return 1


@pytest.fixture
def channel():
    return "the channel"


@pytest.fixture
def track_title():
    return "not the title!"


@pytest.fixture
def artist():
    return "not the channel"


@pytest.fixture
def mock_youtube_video_to_dict(
    mock_entry_to_dict, playlist_index, playlist_size, channel, track_title, artist
):
    return dict(
        mock_entry_to_dict,
        **{
            "playlist_index": playlist_index,
            "playlist_size": playlist_size,
            "channel": channel,
            "channel_sanitized": channel,
            "track_title": track_title,
            "track_title_sanitized": track_title,
            "artist": artist,
            "artist_sanitized": artist,
        }
    )


@pytest.fixture
def mock_youtube_video_kwargs(
    mock_entry_kwargs, playlist_index, playlist_size, channel, track_title, artist
):
    return dict(
        mock_entry_kwargs,
        **{
            "playlist_index": playlist_index,
            "playlist_count": playlist_size,
            "channel": channel,
            "track": track_title,
            "artist": artist,
        }
    )


@pytest.fixture
def mock_youtube_video(mock_youtube_video_kwargs):
    return YoutubeVideo(entry_dict=mock_youtube_video_kwargs)


class TestYoutubeVideo(object):
    def test_to_dict(self, mock_youtube_video, mock_youtube_video_to_dict):
        assert mock_youtube_video.to_dict() == mock_youtube_video_to_dict

    def test_youtube_dict_contains_valid_formatters(
        self, mock_youtube_video, validate_entry_dict_contains_valid_formatters
    ):
        assert validate_entry_dict_contains_valid_formatters(mock_youtube_video)
