import pytest
from e2e.expected_download import assert_expected_downloads
from e2e.expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def single_video_subs_embed_preset_dict(output_directory):
    return {
        "preset": "yt_music_video",
        "youtube": {"video_url": "https://www.youtube.com/watch?v=2lAe1cqCOXo"},
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        "subtitles": {
            "embed_subtitles": True,
            "languages": ["en", "de"],
            "allow_auto_generated_subtitles": True,
        },
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
        },
        "overrides": {"artist": "JMC"},
    }


@pytest.fixture
def test_single_video_subs_embed_and_file_preset_dict(single_video_subs_embed_preset_dict):
    single_video_subs_embed_preset_dict["subtitles"][
        "subtitles_name"
    ] = "{music_video_name}.{lang}.{subtitles_ext}"
    return single_video_subs_embed_preset_dict


class TestSubtitles:
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_subtitles_embedded(
        self,
        music_video_config,
        single_video_subs_embed_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=music_video_config,
            preset_name="subtitles_embedded_test",
            preset_dict=single_video_subs_embed_preset_dict,
        )

        transaction_log = subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/test_subtitles_embedded.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="plugins/test_subtitles_embedded.json",
        )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_subtitles_embedded_and_file(
        self,
        music_video_config,
        test_single_video_subs_embed_and_file_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=music_video_config,
            preset_name="subtitles_embedded_and_file_test",
            preset_dict=test_single_video_subs_embed_and_file_preset_dict,
        )

        transaction_log = subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/test_subtitles_embedded_and_file.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="plugins/test_subtitles_embedded_and_file.json",
        )
