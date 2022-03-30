import pytest

from ytdl_subscribe.entries.entry import Entry


@pytest.fixture
def uid():
    return "abc123"


@pytest.fixture
def title():
    return "entry title"


@pytest.fixture
def upload_year():
    return 2021


@pytest.fixture
def upload_date(upload_year):
    return f"{upload_year}-01-06"


@pytest.fixture
def ext():
    return "mp5"


@pytest.fixture
def thumbnail_ext():
    return "yall"


@pytest.fixture
def thumbnail(thumbnail_ext):
    return f"thumb.{thumbnail_ext}"


@pytest.fixture
def download_file_name(uid, ext):
    return f"{uid}.{ext}"


@pytest.fixture
def mock_entry_to_dict(
    uid, title, ext, upload_date, upload_year, thumbnail, thumbnail_ext
):
    return {
        "uid": uid,
        "title": title,
        "sanitized_title": title,
        "ext": ext,
        "upload_date": upload_date,
        "upload_year": upload_year,
        "thumbnail": thumbnail,
        "thumbnail_ext": thumbnail_ext,
    }


@pytest.fixture
def mock_entry_kwargs(uid, title, ext, upload_date, thumbnail):
    return {
        "id": uid,
        "title": title,
        "ext": ext,
        "upload_date": upload_date,
        "thumbnail": thumbnail,
    }


@pytest.fixture
def mock_entry(mock_entry_kwargs):
    return Entry(**mock_entry_kwargs)
