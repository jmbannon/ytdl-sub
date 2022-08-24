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
    return "entry title"


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
):
    return {
        "uid": uid,
        "title": title,
        "title_sanitized": title,
        "ext": ext,
        "extractor": extractor,
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
        "thumbnail_ext": thumbnail_ext,
    }


@pytest.fixture
def mock_entry_kwargs(uid, title, ext, upload_date, extractor, download_thumbnail_name):
    return {
        "id": uid,
        "extractor": extractor,
        "title": title,
        "ext": ext,
        "upload_date": upload_date,
        "thumbnail": download_thumbnail_name,
    }


@pytest.fixture
def mock_entry(mock_entry_kwargs):
    return Entry(entry_dict=mock_entry_kwargs, working_directory=".")


@pytest.fixture
def validate_entry_dict_contains_valid_formatters():
    def _validate_entry_dict_contains_valid_formatters(entry: Entry):
        for key, value in entry.to_dict().items():
            expected_string = f"test {value} formatting works"
            formatter = StringFormatterValidator(
                name="test", value=f"test {{{key}}} formatting works"
            )

            assert formatter.apply_formatter(entry.to_dict()) == expected_string

        return True

    return _validate_entry_dict_contains_valid_formatters
