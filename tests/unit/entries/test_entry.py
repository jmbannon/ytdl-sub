import tempfile

import pytest

from ytdl_subscribe.validators.base.string_formatter_validators import StringFormatterValidator
from ytdl_subscribe.validators.exceptions import StringFormattingException


class TestEntry(object):
    def test_entry_properties(
        self,
        mock_entry,
        validate_entry_properties,
    ):
        assert validate_entry_properties(mock_entry)

    def test_entry_to_dict(self, mock_entry, mock_entry_to_dict):
        assert mock_entry.to_dict() == mock_entry_to_dict

    def test_entry_dict_contains_valid_formatters(
        self, mock_entry, validate_entry_dict_contains_valid_formatters
    ):
        assert validate_entry_dict_contains_valid_formatters(mock_entry)

    def test_entry_file_path(self, mock_entry, download_file_name):
        relative_directory = tempfile.TemporaryDirectory()

        try:
            file_path = mock_entry.file_path(relative_directory.name)
            assert isinstance(file_path, str)
            assert file_path == f"{relative_directory.name}/{download_file_name}"
        finally:
            relative_directory.cleanup()

    def test_entry_missing_kwarg(self, mock_entry):
        key = "dne"
        expected_error_msg = f"Expected '{key}' in Entry but does not exist."

        assert mock_entry.kwargs_contains(key) is False
        with pytest.raises(KeyError, match=expected_error_msg):
            mock_entry.kwargs(key)

    def test_entry_formatter_fails_missing_field(self, mock_entry):
        format_string = StringFormatterValidator(name="test", value=f"prefix {{bah_humbug}} suffix")
        available_fields = ", ".join(sorted(mock_entry.to_dict().keys()))
        expected_error_msg = (
            f"Validation error in test: Format variable 'bah_humbug' does not exist. "
            f"Available variables: {available_fields}"
        )

        with pytest.raises(StringFormattingException, match=expected_error_msg):
            assert mock_entry.apply_formatter(format_string)
