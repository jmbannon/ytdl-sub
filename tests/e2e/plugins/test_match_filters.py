import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches
from resources import DISABLE_YOUTUBE_TESTS

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def preset_dict(output_directory):
    return {
        "preset": "Jellyfin Music Videos",
        "download": "https://www.youtube.com/watch?v=2zYF9JLHDmA",
        "output_options": {"output_directory": output_directory},
        "format": "worst[ext=mp4]",  # download the worst format so it is fast
        "ytdl_options": {
            "postprocessor_args": {"ffmpeg": ["-bitexact"]},  # Must add this for reproducibility
        },
        "match_filters": {"filters": ["is_live", "view_count <=? 10"]},
    }


@pytest.fixture
def playlist_preset_dict(output_directory):
    return {
        "preset": "Jellyfin Music Videos",
        "download": "https://www.youtube.com/playlist?list=PL5BC0FC26BECA5A35",
        "output_options": {"output_directory": output_directory},
        "format": "worst[ext=mp4]",  # download the worst format so it is fast
        "ytdl_options": {
            "postprocessor_args": {"ffmpeg": ["-bitexact"]},  # Must add this for reproducibility
        },
        "match_filters": {"filters": ["view_count > 20000"]},
    }


@pytest.fixture
def livestream_preset_dict(output_directory):
    return {
        "preset": "Jellyfin Music Videos",
        "download": "https://www.youtube.com/watch?v=DoUOrTJbIu4",
        "output_options": {"output_directory": output_directory},
        "ytdl_options": {
            "postprocessor_args": {"ffmpeg": ["-bitexact"]},
        },
    }


@pytest.mark.skipif(DISABLE_YOUTUBE_TESTS, reason="YouTube tests cannot run in GH")
class TestFileConvert:
    def test_livestreams_download_filtered(
        self,
        default_config,
        livestream_preset_dict,
        output_directory,
    ):
        subscription = Subscription.from_dict(
            config=default_config,
            preset_name="match_filter_test",
            preset_dict=livestream_preset_dict,
        )

        transaction_log = subscription.download(dry_run=False)
        assert transaction_log.is_empty

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_match_filters_empty(
        self,
        default_config,
        preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=default_config,
            preset_name="match_filter_test",
            preset_dict=preset_dict,
        )

        transaction_log = subscription.download(dry_run=dry_run)
        assert transaction_log.is_empty

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_match_filters_partial(
        self,
        default_config,
        playlist_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=default_config,
            preset_name="match_filter_test",
            preset_dict=playlist_preset_dict,
        )

        transaction_log = subscription.download(dry_run=dry_run)

        summary_path = "plugins/match_filters"
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"{summary_path}/test_match_filters_partial.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name=f"{summary_path}/test_match_filters_partial.json",
        )
