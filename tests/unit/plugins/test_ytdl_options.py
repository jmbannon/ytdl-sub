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


class TestYtdlOptions:
    def test_cookiefile_does_not_exist(
        self,
        default_config: ConfigFile,
        preset_dict: Dict[str, Any],
    ):
        preset_dict["ytdl_options"] = {
            "cookiefile": "/path/to/nowhere",
        }

        error_msg = "Specified cookiefile /path/to/nowhere but it does not exist as a file."

        with pytest.raises(ValidationException, match=re.escape(error_msg)):
            Subscription.from_dict(
                config=default_config,
                preset_name="test_ytdl_options",
                preset_dict=preset_dict,
            ).download(dry_run=False)
