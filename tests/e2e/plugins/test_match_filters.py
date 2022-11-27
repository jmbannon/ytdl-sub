import pytest

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def preset_dict(output_directory):
    return {
        "preset": "music_video",
        "download": {"url": "https://www.youtube.com/watch?v=2zYF9JLHDmA"},
        "output_options": {"output_directory": output_directory},
        # download the worst format so it is fast
        "ytdl_options": {
            "postprocessor_args": {"ffmpeg": ["-bitexact"]},  # Must add this for reproducibility
        },
        "match_filters": {"filters": ["is_live", "view_count <=? 10"]},
    }


class TestFileConvert:
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_match_filters(
        self,
        music_video_config,
        preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=music_video_config,
            preset_name="match_filter_test",
            preset_dict=preset_dict,
        )

        transaction_log = subscription.download(dry_run=dry_run)
        assert transaction_log.is_empty
