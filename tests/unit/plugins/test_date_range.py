import re
from typing import Any
from typing import Dict

import pytest
from conftest import get_match_filters

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ValidationException


@pytest.fixture
def preset_dict(output_directory) -> Dict[str, Any]:
    return {
        "download": "https://your.name.here",
        "output_options": {"output_directory": output_directory, "file_name": "will_error.mp4"},
    }


class TestDateRange:
    @pytest.mark.parametrize("date_range_type", ["upload_date", "release_date"])
    def test_date_range_type(
        self,
        default_config: ConfigFile,
        preset_dict: Dict[str, Any],
        output_directory: str,
        date_range_type: str,
    ):
        preset_dict["date_range"] = {
            "before": "20250530",
            "after": "20250510",
            "type": date_range_type,
        }
        sub = Subscription.from_dict(
            config=default_config,
            preset_name="test_date_range",
            preset_dict=preset_dict,
        )

        metadata_filter, metadata_breaking_filter = get_match_filters(
            subscription=sub, dry_run=False, download_filters=False
        )
        assert metadata_filter == [
            f"!is_live & !is_upcoming & !post_live & {date_range_type} < 20250530"
        ]
        assert metadata_breaking_filter == [f"{date_range_type} >= 20250510"]

        download_filter, download_breaking_filter = get_match_filters(
            subscription=sub, dry_run=False, download_filters=True
        )
        assert not download_filter
        assert not download_breaking_filter

    def test_date_range_breaks_false(
        self,
        default_config: ConfigFile,
        preset_dict: Dict[str, Any],
        output_directory: str,
    ):
        preset_dict["date_range"] = {
            "before": "20250530",
            "after": "20250510",
            "breaks": False,
        }
        sub = Subscription.from_dict(
            config=default_config,
            preset_name="test_date_range",
            preset_dict=preset_dict,
        )

        metadata_filter, metadata_breaking_filter = get_match_filters(
            subscription=sub, dry_run=False, download_filters=False
        )
        assert metadata_filter == [
            f"!is_live & !is_upcoming & !post_live & upload_date < 20250530 & upload_date >= 20250510"
        ]
        assert not metadata_breaking_filter

        download_filter, download_breaking_filter = get_match_filters(
            subscription=sub, dry_run=False, download_filters=True
        )
        assert not download_filter
        assert not download_breaking_filter

    def test_date_range_invalid_type(
        self,
        default_config: ConfigFile,
        preset_dict: Dict[str, Any],
        output_directory: str,
    ):
        preset_dict["date_range"] = {
            "before": "20250530",
            "after": "20250510",
            "type": "no",
        }

        error_msg = (
            "Validation error in test_date_range.date_range.type: "
            "Must be one of the following values: release_date, upload_date"
        )

        with pytest.raises(ValidationException, match=re.escape(error_msg)):
            Subscription.from_dict(
                config=default_config,
                preset_name="test_date_range",
                preset_dict=preset_dict,
            ).download(dry_run=False)
