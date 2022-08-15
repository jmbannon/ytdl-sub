import pytest
from e2e.expected_download import assert_expected_downloads
from e2e.expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def single_video_sponsorblock_and_embedded_subs_preset_dict(output_directory):
    return {
        "preset": "yt_music_video",
        "youtube": {"video_url": "https://www.youtube.com/watch?v=-wJOUAuKZm8"},
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        "subtitles": {
            "embed_subtitles": True,
            "languages": ["en", "de"],
            "allow_auto_generated_subtitles": True,
        },
        "chapters": {
            "sponsorblock_categories": [
                "outro",
                "selfpromo",
                "preview",
                "interaction",
                "sponsor",
                "music_offtopic",
                "intro",
            ],
            "remove_sponsorblock_categories": "all",
            "remove_chapters_regex": [
                "Intro",
                "Outro",
            ],
        },
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
        },
        "overrides": {"artist": "JMC"},
    }


class TestChapters:
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_chapters_sponsorblock_and_removal_with_subs(
        self,
        music_video_config,
        single_video_sponsorblock_and_embedded_subs_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=music_video_config,
            preset_name="sponsorblock_with_embedded_subs_test",
            preset_dict=single_video_sponsorblock_and_embedded_subs_preset_dict,
        )

        transaction_log = subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/test_chapters_sb_and_embedded_subs.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="plugins/test_chapters_sb_and_embedded_subs.json",
        )
