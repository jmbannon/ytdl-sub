import re
from typing import Any
from typing import Dict

import pytest
import yt_dlp
from conftest import assert_logs

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.ffmpeg import FFMPEG


@pytest.fixture
def preset_dict(output_directory) -> Dict[str, Any]:
    return {
        "download": "https://your.name.here",
        "output_options": {"output_directory": output_directory, "file_name": "will_error.mp4"},
    }


class TestYtdlOptions:

    def test_ytdl_options_are_strings(
        self,
        default_config: ConfigFile,
        preset_dict: Dict[str, Any],
        working_directory,
    ):
        expected_ytdl_options = {
            "ignoreerrors": True,
            "outtmpl": f"{working_directory}/test_ytdl_options/%(id)S.%(ext)s",
            "writethumbnail": False,
            "ffmpeg_location": FFMPEG.ffmpeg_path(),
            "match_filter": yt_dlp.utils.match_filter_func(
                ["!is_live & !is_upcoming & !post_live"], []
            ),
            "skip_download": True,
            "writeinfojson": True,
            "extract_flat": "discard",
        }

        with (
            assert_logs(
                logger=YTDLP.logger,
                expected_message=f"ytdl_options: {str(expected_ytdl_options)}",
                log_level="debug",
                expected_occurrences=1,
            ),
        ):
            _ = Subscription.from_dict(
                config=default_config,
                preset_name="test_ytdl_options",
                preset_dict=preset_dict,
            ).download(dry_run=True)

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
