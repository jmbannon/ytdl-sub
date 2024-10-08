import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches
from resources import DISABLE_YOUTUBE_TESTS

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def single_preset_dict(output_directory):
    return {
        "preset": "Single",
        # test multi-tags
        "music_tags": {"genres": ["multi_tag_1", "multi_tag_2"]},
        # test the new embed_thumbnail plugin
        "embed_thumbnail": True,
        "audio_extract": {"codec": "mp3", "quality": 320},
        "ytdl_options": {
            "postprocessor_args": {"ffmpeg": ["-bitexact"]},  # Must add this for reproducibility
        },
        "overrides": {
            "track_artist": "YouTube",
            "url": "https://www.youtube.com/watch?v=2lAe1cqCOXo",
            "music_directory": output_directory,
        },
    }


@pytest.fixture
def single_best_format_preset_dict(single_preset_dict):
    return dict(single_preset_dict, **{"audio_extract": {"codec": "best"}})


@pytest.fixture
def youtube_release_preset_dict(output_directory):
    return {
        "preset": "YouTube Releases",
        "audio_extract": {"codec": "vorbis", "quality": 140},
        "ytdl_options": {
            "postprocessor_args": {"ffmpeg": ["-bitexact"]},  # Must add this for reproducibility
        },
        "overrides": {
            "track_artist": "Project Zombie",
            "url": "https://youtube.com/playlist?list=PL5BC0FC26BECA5A35",
            "music_directory": output_directory,
        },
    }


@pytest.mark.skipif(DISABLE_YOUTUBE_TESTS, reason="YouTube tests cannot run in GH")
class TestAudioExtract:
    @pytest.mark.parametrize("dry_run", [False])
    def test_audio_extract_single_song(
        self,
        default_config,
        single_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=default_config,
            preset_name="single_song_test",
            preset_dict=single_preset_dict,
        )

        transaction_log = subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/test_audio_extract_single.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="plugins/test_audio_extract_single.json",
        )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_audio_extract_single_song_best_format(
        self,
        default_config,
        single_best_format_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=default_config,
            preset_name="single_song_best_test",
            preset_dict=single_best_format_preset_dict,
        )

        transaction_log = subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"plugins/test_audio_extract_single_best{'_dry_run' if dry_run else ''}.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name=f"plugins/test_audio_extract_single_best{'_dry_run' if dry_run else ''}.json",
        )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_audio_extract_multiple_songs(
        self,
        default_config,
        youtube_release_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=default_config,
            preset_name="multiple_songs_test",
            preset_dict=youtube_release_preset_dict,
        )

        transaction_log = subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/test_audio_extract_playlist.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="plugins/test_audio_extract_playlist.json",
        )
