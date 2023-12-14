import pytest

from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions

v: VariableDefinitions = VARIABLES


class TestEntry(object):
    def test_entry_to_dict(self, mock_entry, mock_entry_to_dict):
        out = mock_entry.to_dict()

        # HACK: Ensure legacy variables are in new output and equal
        for key, expected_value in mock_entry_to_dict.items():
            assert out[key] == expected_value, f"{key} does not equal"

    @pytest.mark.parametrize(
        "upload_date, year_rev, month_rev, day_rev, month_rev_pad, day_rev_pad",
        [
            ("20000228", 100, 11, 2, "11", "02"),
            ("20200808", 80, 5, 24, "05", "24"),
        ],
    )
    def test_entry_reverse_variables(
        self,
        mock_entry_kwargs,
        upload_date,
        year_rev,
        month_rev,
        day_rev,
        month_rev_pad,
        day_rev_pad,
    ):

        mock_entry_kwargs["upload_date"] = upload_date
        entry = Entry(entry_dict=mock_entry_kwargs, working_directory=".").initialize_script()
        assert entry.get(v.upload_year_truncated_reversed, int) == year_rev
        assert entry.get(v.upload_month_reversed, int) == month_rev
        assert entry.get(v.upload_day_reversed, int) == day_rev
        assert entry.get(v.upload_month_reversed_padded, str) == month_rev_pad
        assert entry.get(v.upload_day_reversed_padded, str) == day_rev_pad

    @pytest.mark.parametrize(
        "upload_date, day_year, day_year_rev, day_year_pad, day_year_rev_pad",
        [
            ("20000228", 59, 308, "059", "308"),
            ("20210808", 220, 146, "220", "146"),
        ],
    )
    def test_entry_upload_day_of_year_variables(
        self, mock_entry_kwargs, upload_date, day_year, day_year_rev, day_year_pad, day_year_rev_pad
    ):
        mock_entry_kwargs["upload_date"] = upload_date
        entry = Entry(entry_dict=mock_entry_kwargs, working_directory=".").initialize_script()

        assert entry.get(v.upload_day_of_year, int) == day_year
        assert entry.get(v.upload_day_of_year_reversed, int) == day_year_rev
        assert entry.get(v.upload_day_of_year_padded, str) == day_year_pad
        assert entry.get(v.upload_day_of_year_reversed_padded, str) == day_year_rev_pad
