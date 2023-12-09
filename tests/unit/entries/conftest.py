import pytest

from ytdl_sub.entries.entry import Entry
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator


@pytest.fixture
def uid():
    return "abc123"


@pytest.fixture
def extractor():
    return "xtract"


@pytest.fixture
def title():
    return "entry {title}"


@pytest.fixture
def upload_date():
    return "20210112"


@pytest.fixture
def ext():
    return "mp5"


@pytest.fixture
def thumbnail_ext():
    return "jpg"


@pytest.fixture
def webpage_url() -> str:
    return "https://yourname.here"


@pytest.fixture
def download_thumbnail_name(uid, thumbnail_ext):
    return f"{uid}.{thumbnail_ext}"


@pytest.fixture
def download_file_name(uid, ext):
    return f"{uid}.{ext}"


@pytest.fixture
def mock_entry_to_dict(
    uid,
    title,
    ext,
    extractor,
    upload_date,
    thumbnail_ext,
    webpage_url,
):
    return {
        "uid": uid,
        "uid_sanitized": uid,
        "epoch": 1596878400,
        "epoch_date": "20200808",
        "epoch_hour": "09",
        "title": "entry ｛title｝",
        "title_sanitized": "entry ｛title｝",
        "ext": ext,
        "description": "",
        "comments": "",
        "requested_subtitles": "",
        "sponsorblock_chapters": "",
        "creator": "abc123",
        "creator_sanitized": "abc123",
        "channel": "abc123",
        "channel_sanitized": "abc123",
        "channel_id": uid,
        "extractor": extractor,
        "extractor_key": "test_extractor_key",
        "uploader": "abc123",
        "uploader_id": "abc123",
        "uploader_url": "https://yourname.here",
        "download_index": 1,
        "download_index_padded6": "000001",
        "upload_date_index": 1,
        "upload_date_index_padded": "01",
        "upload_date_index_reversed": 99,
        "upload_date_index_reversed_padded": "99",
        "upload_date": upload_date,
        "upload_date_standardized": "2021-01-12",
        "upload_year": 2021,
        "upload_year_truncated": 21,
        "upload_year_truncated_reversed": 79,
        "upload_month": 1,
        "upload_month_padded": "01",
        "upload_month_reversed": 12,
        "upload_month_reversed_padded": "12",
        "upload_day": 12,
        "upload_day_padded": "12",
        "upload_day_reversed": 20,
        "upload_day_reversed_padded": "20",
        "upload_day_of_year": 12,
        "upload_day_of_year_padded": "012",
        "upload_day_of_year_reversed": 354,
        "upload_day_of_year_reversed_padded": "354",
        "thumbnail_ext": thumbnail_ext,
        "info_json_ext": "info.json",
        "webpage_url": webpage_url,
        "playlist_index": 1,
        "playlist_index_padded": "01",
        "playlist_index_padded6": "000001",
        "playlist_index_reversed": 1,
        "playlist_index_reversed_padded": "01",
        "playlist_index_reversed_padded6": "000001",
        "playlist_count": 1,
        "playlist_max_upload_year": 2021,
        "playlist_max_upload_year_truncated": 21,
        "playlist_title": "entry ｛title｝",
        "playlist_title_sanitized": "entry ｛title｝",
        "playlist_description": "",
        "playlist_webpage_url": "https://yourname.here",
        "playlist_uid": "abc123",
        "playlist_uploader": "abc123",
        "playlist_uploader_sanitized": "abc123",
        "playlist_uploader_id": "abc123",
        "playlist_uploader_url": "https://yourname.here",
        "source_count": 1,
        "source_description": "",
        "source_index": 1,
        "source_index_padded": "01",
        "source_title": "entry ｛title｝",
        "source_title_sanitized": "entry ｛title｝",
        "source_webpage_url": "https://yourname.here",
        "source_uid": "abc123",
        "source_uploader": "abc123",
        "source_uploader_id": "abc123",
        "source_uploader_url": "https://yourname.here",
        "uid_sanitized_plex": "abc１２３",
        "title_sanitized_plex": "entry ｛title｝",
        "release_date": upload_date,
        "release_date_standardized": "2021-01-12",
        "release_year": 2021,
        "release_year_truncated": 21,
        "release_year_truncated_reversed": 79,
        "release_month": 1,
        "release_month_padded": "01",
        "release_month_reversed": 12,
        "release_month_reversed_padded": "12",
        "release_day": 12,
        "release_day_padded": "12",
        "release_day_reversed": 20,
        "release_day_reversed_padded": "20",
        "release_day_of_year": 12,
        "release_day_of_year_padded": "012",
        "release_day_of_year_reversed": 354,
        "release_day_of_year_reversed_padded": "354",
    }


@pytest.fixture
def mock_entry_kwargs(
    uid, title, ext, upload_date, extractor, download_thumbnail_name, webpage_url
):
    return {
        "id": uid,
        "epoch": 1596878400,
        "extractor": extractor,
        "extractor_key": "test_extractor_key",
        "title": title,
        "ext": ext,
        "upload_date": upload_date,
        "thumbnail": download_thumbnail_name,
        "webpage_url": webpage_url,
    }


@pytest.fixture
def mock_entry(mock_entry_kwargs):
    return Entry(entry_dict=mock_entry_kwargs, working_directory=".").initialize_script(
        override_variables={},
        unresolvable=set(),
    )
