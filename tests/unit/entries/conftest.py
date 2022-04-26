import pytest

from ytdl_sub.entries.entry import Entry
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator


def _pad(num):
    if num < 10:
        return f"0{num}"
    return str(num)


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
def description():
    return "a description"


@pytest.fixture
def upload_year():
    return 2021


@pytest.fixture
def upload_month():
    return 1


@pytest.fixture
def upload_day():
    return 12


@pytest.fixture
def upload_date(upload_year, upload_month, upload_day):
    return f"{upload_year}{_pad(upload_month)}{_pad(upload_day)}"


@pytest.fixture
def ext():
    return "mp5"


@pytest.fixture
def thumbnail_ext():
    return "yall"


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
    upload_year,
    thumbnail_ext,
    description,
    upload_month,
    upload_day,
):
    return {
        "uid": uid,
        "title": title,
        "sanitized_title": title,
        "ext": ext,
        "extractor": extractor,
        "upload_date": upload_date,
        "upload_date_standardized": f"{upload_year}-{_pad(upload_month)}-{_pad(upload_day)}",
        "upload_year": upload_year,
        "upload_month": upload_month,
        "upload_month_padded": _pad(upload_month),
        "upload_day": upload_day,
        "upload_day_padded": _pad(upload_day),
        "thumbnail_ext": thumbnail_ext,
        "description": description,
    }


@pytest.fixture
def mock_entry_kwargs(
    uid, title, ext, upload_date, extractor, description, download_thumbnail_name
):
    return {
        "id": uid,
        "extractor": extractor,
        "title": title,
        "ext": ext,
        "upload_date": upload_date,
        "thumbnail": download_thumbnail_name,
        "description": description,
    }


@pytest.fixture
def mock_entry(mock_entry_kwargs):
    return Entry(entry_dict=mock_entry_kwargs)


@pytest.fixture
def validate_entry_properties(
    uid,
    title,
    upload_date,
    upload_year,
    ext,
    extractor,
    thumbnail_ext,
    download_file_name,
    download_thumbnail_name,
):
    def _validate_entry_properties(entry: Entry):
        assert entry.uid == uid
        assert entry.title == title
        assert entry.sanitized_title == title
        assert entry.upload_date == upload_date
        assert entry.upload_year == upload_year
        assert entry.ext == ext
        assert entry.thumbnail_ext == thumbnail_ext
        assert entry.extractor == extractor

        return True

    return _validate_entry_properties


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
