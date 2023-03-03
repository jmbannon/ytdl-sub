import sys
from unittest.mock import patch

import pytest

from ytdl_sub.cli.main import main
from ytdl_sub.utils.exceptions import ValidationException


def test_args_after_sub_work():
    with patch.object(
        sys,
        "argv",
        ["ytdl-sub", "-c", "examples/tv_show_config.yaml", "sub", "--log-level", "debug"],
    ), patch("ytdl_sub.cli.main._download_subscriptions_from_yaml_files") as mock_sub:
        main()

        assert mock_sub.call_count == 1
        assert mock_sub.call_args.kwargs["args"].config == "examples/tv_show_config.yaml"
        assert mock_sub.call_args.kwargs["args"].subscription_paths == ["subscriptions.yaml"]
        assert mock_sub.call_args.kwargs["args"].ytdl_sub_log_level == "debug"
