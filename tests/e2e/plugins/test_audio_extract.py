import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def single_song_preset_dict(output_directory):
    return {
        "preset": "single",
        # test multi-tags
        "music_tags": {"embed_thumbnail": True, "tags": {"genres": ["multi_tag_1", "multi_tag_2"]}},
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
            "postprocessor_args": {"ffmpeg": ["-bitexact"]},  # Must add this for reproducibility
        },
        "overrides": {
            "url": "https://www.youtube.com/watch?v=2lAe1cqCOXo",
            "music_directory": output_directory,
        },
    }


@pytest.fixture
def multiple_songs_preset_dict(output_directory):
    return {
        "preset": "albums_from_playlists",
        "audio_extract": {"codec": "vorbis", "quality": 140},
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
            "postprocessor_args": {"ffmpeg": ["-bitexact"]},  # Must add this for reproducibility
        },
        "overrides": {
            "url": "https://youtube.com/playlist?list=PL5BC0FC26BECA5A35",
            "music_directory": output_directory,
        },
    }


class TestAudioExtract:
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_audio_extract_single_song(
        self,
        music_audio_config,
        single_song_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=music_audio_config,
            preset_name="single_song_test",
            preset_dict=single_song_preset_dict,
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
    def test_audio_extract_multiple_songs(
        self,
        music_audio_config,
        multiple_songs_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=music_audio_config,
            preset_name="multiple_songs_test",
            preset_dict=multiple_songs_preset_dict,
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
