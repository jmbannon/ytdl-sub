import pytest

from ytdl_subscribe.entries.entry import Entry
from ytdl_subscribe.validators.base.string_formatter_validators import StringFormatterValidator


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
def mock_entry_to_dict(uid, title, ext, upload_date, upload_year, thumbnail, thumbnail_ext):
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


@pytest.fixture
def validate_entry_properties(
    uid,
    title,
    upload_date,
    upload_year,
    ext,
    thumbnail,
    thumbnail_ext,
    download_file_name,
):
    def _validate_entry_properties(entry: Entry):
        assert entry.uid == uid
        assert entry.title == title
        # Title does not require sanitizing, so should be the same
        assert entry.sanitized_title == title
        assert entry.upload_date == upload_date
        assert entry.upload_year == upload_year
        assert entry.ext == ext
        assert entry.thumbnail == thumbnail
        assert entry.thumbnail_ext == thumbnail_ext
        assert entry.download_file_name == download_file_name

        return True

    return _validate_entry_properties


@pytest.fixture
def validate_entry_dict_contains_valid_formatters():
    def _validate_entry_dict_contains_valid_formatters(entry: Entry):
        for key, value in entry.to_dict().items():
            expected_string = f"test {value} formatting works"
            format_string = f"test {{{key}}} formatting works"

            assert (
                entry.apply_formatter(StringFormatterValidator(name="test", value=format_string))
                == expected_string
            )

        return True

    return _validate_entry_dict_contains_valid_formatters
