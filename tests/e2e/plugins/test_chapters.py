from typing import Dict

import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def sponsorblock_and_subs_preset_dict(output_directory) -> Dict:
    return {
        "preset": "music_video",
        "download": "https://www.youtube.com/watch?v=-wJOUAuKZm8",
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
            "postprocessor_args": {"ffmpeg": ["-bitexact"]},  # Must add this for reproducibility
        },
        "overrides": {"artist": "JMC"},
    }


@pytest.fixture
def chapters_from_comments_preset_dict(sponsorblock_and_subs_preset_dict: Dict) -> Dict:
    sponsorblock_and_subs_preset_dict["download"] = "https://www.youtube.com/watch?v=MO5AWAqe01Y"
    sponsorblock_and_subs_preset_dict["chapters"] = {
        "embed_chapters": True,
        "allow_chapters_from_comments": True,
    }
    return sponsorblock_and_subs_preset_dict


class TestChapters:
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_chapters_sponsorblock_and_removal_with_subs(
        self,
        music_video_config,
        sponsorblock_and_subs_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=music_video_config,
            preset_name="sponsorblock_with_embedded_subs_test",
            preset_dict=sponsorblock_and_subs_preset_dict,
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
            ignore_md5_hashes_for=[
                "JMC/JMC - This GPU SLIDES into this Case! - Silverstone SUGO 16 ITX Case.mp4"
            ],
        )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_chapters_from_comments(
        self,
        music_video_config,
        chapters_from_comments_preset_dict,
        timestamps_file_path,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=music_video_config,
            preset_name="chapters_from_comments",
            preset_dict=chapters_from_comments_preset_dict,
        )

        transaction_log = subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/chapters/test_chapters_from_comments.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="plugins/chapters/test_chapters_from_comments.json",
            ignore_md5_hashes_for=["JMC/JMC - Move 78 - Automated Improvisation [Full Album].mp4"],
        )
