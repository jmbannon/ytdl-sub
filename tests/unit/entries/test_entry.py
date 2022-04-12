import pytest


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

    def test_entry_missing_kwarg(self, mock_entry):
        key = "dne"
        expected_error_msg = f"Expected '{key}' in Entry but does not exist."

        assert mock_entry.kwargs_contains(key) is False
        with pytest.raises(KeyError, match=expected_error_msg):
            mock_entry.kwargs(key)
