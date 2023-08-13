import re

import mergedeep
import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ValidationException


@pytest.fixture
def yt_album_as_chapters_preset_dict(output_directory):
    return {
        "preset": "albums_from_chapters",
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
            "postprocessor_args": {"ffmpeg": ["-bitexact"]},  # Must add this for reproducibility
        },
        "overrides": {
            "url": "https://www.youtube.com/watch?v=zeR2_YjlXWA",
            "music_directory": output_directory,
        },
    }


@pytest.fixture
def yt_album_as_chapters_with_regex_preset_dict(yt_album_as_chapters_preset_dict):
    mergedeep.merge(
        yt_album_as_chapters_preset_dict,
        {
            "regex": {
                "from": {
                    # Ensure regex can handle override variables that come from the
                    # post-metadata stage
                    "override_chapter_title": {
                        "match": r"\d+\. (.+)",
                        "capture_group_names": "captured_track_title",
                        "capture_group_defaults": "{chapter_title}",
                    },
                    "title": {
                        "match": [
                            "(.+) - (.+) [-[\\(\\{].+",
                            "(.+) - (.+)",
                        ],
                        "capture_group_names": [
                            "captured_track_artist",
                            "captured_track_album",
                        ],
                        "capture_group_defaults": [
                            "{channel}",
                            "{title}",
                        ],
                    },
                }
            },
            "overrides": {
                "override_chapter_title": "{chapter_title}",
                "track_title": "{captured_track_title}",
                "track_album": "{captured_track_album}",
                "track_artist": "{captured_track_artist}",
            },
        },
    )
    return yt_album_as_chapters_preset_dict


class TestSplitByChapters:
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_video_with_chapters(
        self,
        music_audio_config,
        yt_album_as_chapters_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=music_audio_config,
            preset_name="split_by_chapters_video",
            preset_dict=yt_album_as_chapters_preset_dict,
        )

        transaction_log = subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"plugins/split_by_chapters_video{'-dry-run' if dry_run else ''}.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="plugins/split_by_chapters_video.json",
        )

        if not dry_run:
            transaction_log = subscription.download()
            assert transaction_log.is_empty

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_video_with_chapters_and_regex(
        self,
        music_audio_config,
        yt_album_as_chapters_with_regex_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=music_audio_config,
            preset_name="split_by_chapters_with_regex_video",
            preset_dict=yt_album_as_chapters_with_regex_preset_dict,
        )

        transaction_log = subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"plugins/split_by_chapters_with_regex_video{'-dry-run' if dry_run else ''}.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="plugins/split_by_chapters_with_regex_video.json",
        )

    @pytest.mark.parametrize("dry_run", [True, False])
    @pytest.mark.parametrize("when_no_chapters", ["pass", "drop", "error"])
    def test_video_with_no_chapters_and_regex(
        self,
        music_audio_config,
        yt_album_as_chapters_with_regex_preset_dict,
        output_directory,
        dry_run,
        when_no_chapters,
    ):
        mergedeep.merge(
            yt_album_as_chapters_with_regex_preset_dict,
            {
                "download": "https://youtube.com/watch?v=HKTNxEqsN3Q",
                "split_by_chapters": {"when_no_chapters": when_no_chapters},
            },
        )

        subscription = Subscription.from_dict(
            config=music_audio_config,
            preset_name="split_by_chapters_with_regex_video",
            preset_dict=yt_album_as_chapters_with_regex_preset_dict,
        )

        if when_no_chapters == "error":
            with pytest.raises(
                ValidationException,
                match=re.escape(
                    "Tried to split 'Oblivion Mod \"Falcor\" p.1' by chapters but it has no chapters"
                ),
            ):
                _ = subscription.download(dry_run=dry_run)
            return

        transaction_log = subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"plugins/split_by_chapters_with_regex_no_chapters_video_{when_no_chapters}.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name=f"plugins/split_by_chapters_with_regex_no_chapters_video_{when_no_chapters}.txt",
        )
