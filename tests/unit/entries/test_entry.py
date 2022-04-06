import tempfile

import pytest

from ytdl_subscribe.validators.base.string_formatter_validators import (
    StringFormatterValidator,
)
from ytdl_subscribe.validators.config.overrides.overrides_validator import (
    OverridesValidator,
)
from ytdl_subscribe.validators.exceptions import StringFormattingException
from ytdl_subscribe.validators.exceptions import ValidationException


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

    def test_entry_formatter_single_field(self, mock_entry):
        format_string = StringFormatterValidator(
            name="test", value=f"prefix {{uid}} suffix"
        )
        expected_string = f"prefix {mock_entry.uid} suffix"

        assert mock_entry.apply_formatter(format_string) == expected_string

    def test_entry_formatter_duplicate_fields(self, mock_entry):
        format_string = StringFormatterValidator(
            name="test", value=f"prefix {{upload_year}} {{upload_year}} suffix"
        )
        expected_string = (
            f"prefix {mock_entry.upload_year} {mock_entry.upload_year} suffix"
        )

        assert mock_entry.apply_formatter(format_string) == expected_string

    def test_entry_formatter_override(self, mock_entry):
        new_uid = "my very own uid"
        overrides = OverridesValidator(name="test", value={"uid": new_uid})

        format_string = StringFormatterValidator(
            name="test", value=f"prefix {{uid}} suffix"
        )
        expected_string = f"prefix {new_uid} suffix"

        assert (
            mock_entry.apply_formatter(format_string, overrides=overrides)
            == expected_string
        )

    def test_entry_formatter_override_recursive(self, mock_entry):
        overrides = OverridesValidator(
            name="test",
            value={
                "level_a": "level a",
                "level_b": "level b and {level_a}",
                "level_c": "level c and {level_b}",
            },
        )

        format_string = StringFormatterValidator(
            name="test", value="level d and {level_c}"
        )
        expected_string = "level d and level c and level b and level a"

        assert (
            mock_entry.apply_formatter(format_string, overrides=overrides)
            == expected_string
        )

    def test_entry_formatter_override_recursive_fail_cycle(self, mock_entry):
        overrides = OverridesValidator(
            name="test",
            value={
                "level_a": "{level_b}",
                "level_b": "{level_a}",
            },
        )

        # Max depth is 3 so should go level_a -(0)-> level_b -(1)-> level_a -(2)-> level_b
        expected_error_msg = (
            "Validation error in test: Attempted to format but failed after reaching max recursion "
            "depth of 3. Try to keep variables dependent on only one other variable at max. "
            "Unresolved variables: level_b"
        )

        format_string = StringFormatterValidator(name="test", value="{level_a}")

        with pytest.raises(StringFormattingException, match=expected_error_msg):
            _ = mock_entry.apply_formatter(format_string, overrides=overrides)

    def test_entry_missing_kwarg(self, mock_entry):
        key = "dne"
        expected_error_msg = f"Expected '{key}' in Entry but does not exist."

        assert mock_entry.kwargs_contains(key) is False
        with pytest.raises(KeyError, match=expected_error_msg):
            mock_entry.kwargs(key)

    def test_entry_formatter_fails_missing_field(self, mock_entry):
        format_string = StringFormatterValidator(
            name="test", value=f"prefix {{bah_humbug}} suffix"
        )
        available_fields = ", ".join(sorted(mock_entry.to_dict().keys()))
        expected_error_msg = (
            f"Validation error in test: Format variable 'bah_humbug' does not exist. "
            f"Available variables: {available_fields}"
        )

        with pytest.raises(StringFormattingException, match=expected_error_msg):
            assert mock_entry.apply_formatter(format_string)
