import pytest

from ytdl_sub.entries.soundcloud import SoundcloudTrack


@pytest.fixture
def url():
    return "soundcloud.com/artist/track-asdfasdf"


@pytest.fixture
def mock_soundcloud_track_to_dict(mock_entry_to_dict):
    return dict(
        mock_entry_to_dict,
        **{
            "track_number": 1,
            "track_number_padded": "01",
            "album": mock_entry_to_dict["title"],
            "album_sanitized": mock_entry_to_dict["title_sanitized"],
            "album_year": mock_entry_to_dict["upload_year"],
            "track_count": 1,
        }
    )


@pytest.fixture
def mock_soundcloud_track_kwargs(mock_entry_kwargs, url):
    return dict(mock_entry_kwargs, **{"url": url})


@pytest.fixture
def mock_soundcloud_track(mock_soundcloud_track_kwargs):
    return SoundcloudTrack(entry_dict=mock_soundcloud_track_kwargs, working_directory=".")


class TestSoundcloudTrack(object):
    def test_to_dict(self, mock_soundcloud_track, mock_soundcloud_track_to_dict):
        assert mock_soundcloud_track.to_dict() == mock_soundcloud_track_to_dict

    def test_soundcloud_dict_contains_valid_formatters(
        self, mock_soundcloud_track, validate_entry_dict_contains_valid_formatters
    ):
        assert validate_entry_dict_contains_valid_formatters(mock_soundcloud_track)
