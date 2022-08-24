import pytest


class TestEntry(object):
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

    @pytest.mark.parametrize(
        "upload_date, year_rev, month_rev, day_rev, month_rev_pad, day_rev_pad",
        [
            ("20000228", 100, 11, 2, "11", "02"),
            ("20200808", 80, 5, 24, "05", "24"),
        ],
    )
    def test_entry_reverse_variables(
        self, mock_entry, upload_date, year_rev, month_rev, day_rev, month_rev_pad, day_rev_pad
    ):
        mock_entry._kwargs["upload_date"] = upload_date

        assert mock_entry.upload_year_truncated_reversed == year_rev
        assert mock_entry.upload_month_reversed == month_rev
        assert mock_entry.upload_day_reversed == day_rev

        assert mock_entry.upload_month_reversed_padded == month_rev_pad
        assert mock_entry.upload_day_reversed_padded == day_rev_pad

    @pytest.mark.parametrize(
        "upload_date, day_year, day_year_rev, day_year_pad, day_year_rev_pad",
        [
            ("20000228", 59, 308, "059", "308"),
            ("20210808", 220, 146, "220", "146"),
        ],
    )
    def test_entry_upload_day_of_year_variables(
        self, mock_entry, upload_date, day_year, day_year_rev, day_year_pad, day_year_rev_pad
    ):
        mock_entry._kwargs["upload_date"] = upload_date

        assert mock_entry.upload_day_of_year == day_year
        assert mock_entry.upload_day_of_year_reversed == day_year_rev
        assert mock_entry.upload_day_of_year_padded == day_year_pad
        assert mock_entry.upload_day_of_year_reversed_padded == day_year_rev_pad
