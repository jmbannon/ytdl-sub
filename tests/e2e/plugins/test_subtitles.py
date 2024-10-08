import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches
from resources import DISABLE_YOUTUBE_TESTS

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def single_video_subs_embed_preset_dict(output_directory):
    return {
        "preset": "Jellyfin Music Videos",
        "download": "https://www.youtube.com/watch?v=2lAe1cqCOXo",
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        "subtitles": {
            "embed_subtitles": True,
            "languages": ["en", "de"],
            "allow_auto_generated_subtitles": True,
        },
        "format": "worst[ext=mp4]",  # download the worst format so it is fast
        "overrides": {"music_video_artist": "JMC"},
    }


@pytest.fixture
def test_single_video_subs_embed_and_file_preset_dict(single_video_subs_embed_preset_dict):
    single_video_subs_embed_preset_dict["subtitles"][
        "subtitles_name"
    ] = "{music_video_file_name}.{lang}.{subtitles_ext}"
    return single_video_subs_embed_preset_dict


@pytest.mark.skipif(DISABLE_YOUTUBE_TESTS, reason="YouTube tests cannot run in GH")
class TestSubtitles:
    def test_subtitle_lang_variable_partial_validates(self, default_config):
        default_config_dict = default_config.as_dict()
        default_config_dict["presets"] = {
            "test_lang_validates": {
                "subtitles": {
                    "embed_subtitles": False,
                    "languages": ["en", "de"],
                    "allow_auto_generated_subtitles": True,
                    "subtitles_name": "{episode_file_path}.{lang}.{subtitles_ext}",
                    "subtitles_type": "srt",
                }
            }
        }

        _ = ConfigFile.from_dict(default_config_dict)

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_subtitles_embedded(
        self,
        default_config,
        single_video_subs_embed_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=default_config,
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
        default_config,
        test_single_video_subs_embed_and_file_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=default_config,
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
