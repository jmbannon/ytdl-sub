import pytest

from ytdl_subscribe.entries.soundcloud import SoundcloudTrack


@pytest.fixture
def track_number():
    return 1


@pytest.fixture
def track_number_padded():
    return "01"


@pytest.fixture
def url():
    return "soundcloud.com/artist/track-asdfasdf"


@pytest.fixture
def is_premiere():
    return False


@pytest.fixture
def mock_soundcloud_track_to_dict(
    mock_entry_to_dict,
    title,
    upload_year,
    track_number,
    track_number_padded,
    is_premiere,
):
    return dict(
        mock_entry_to_dict,
        **{
            "track_number": track_number,
            "track_number_padded": track_number_padded,
            "album": title,
            "sanitized_album": title,
            "album_year": upload_year,
            "is_premiere": is_premiere,
        }
    )


@pytest.fixture
def mock_soundcloud_track_kwargs(mock_entry_kwargs, url):
    return dict(mock_entry_kwargs, **{"url": url})


@pytest.fixture
def mock_soundcloud_track(mock_soundcloud_track_kwargs):
    return SoundcloudTrack(**mock_soundcloud_track_kwargs)


@pytest.fixture
def validate_soundcloud_track_properties(
    validate_entry_properties,
    title,
    upload_year,
    track_number,
    track_number_padded,
    is_premiere,
):
    def _validate_soundcloud_track_properties(soundcloud_track: SoundcloudTrack):
        assert validate_entry_properties(soundcloud_track)
        assert soundcloud_track.track_number == track_number
        assert soundcloud_track.track_number_padded == track_number_padded
        assert soundcloud_track.album == title
        assert soundcloud_track.sanitized_album == title
        assert soundcloud_track.album_year == upload_year
        assert soundcloud_track.is_premiere == is_premiere

        return True

    return _validate_soundcloud_track_properties


class TestSoundcloudTrack(object):
    def test_properties(
        self,
        mock_soundcloud_track,
        validate_soundcloud_track_properties,
    ):
        assert validate_soundcloud_track_properties(mock_soundcloud_track)

    def test_to_dict(self, mock_soundcloud_track, mock_soundcloud_track_to_dict):
        assert mock_soundcloud_track.to_dict() == mock_soundcloud_track_to_dict

    def test_soundcloud_dict_contains_valid_formatters(
        self, mock_soundcloud_track, validate_entry_dict_contains_valid_formatters
    ):
        assert validate_entry_dict_contains_valid_formatters(mock_soundcloud_track)
