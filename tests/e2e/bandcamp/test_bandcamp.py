import pytest
from conftest import assert_logs
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def subscription_dict(output_directory):
    return {
        "preset": "Bandcamp",
        "ytdl_options": {
            # Test that ytdl-options can handle overrides
            # TODO: Move this to a local test
            "max_downloads": "{max_downloads}",
            "extractor_args": {"youtube": {"lang": ["en"]}},
        },
        "audio_extract": {"codec": "mp3", "quality": 320},
        "date_range": {"after": "20210110"},
        "overrides": {
            "subscription_value": "https://sithuayemusic.bandcamp.com/",
            "subscription_indent_1": "Progressive Metal",
            "music_directory": output_directory,
            "max_downloads": 15,
        },
    }


class TestBandcamp:
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_prebuilt_preset_download(
        self,
        subscription_dict,
        default_config,
        output_directory,
        dry_run,
    ):
        discography_subscription = Subscription.from_dict(
            preset_dict=subscription_dict,
            preset_name="Sithu Aye",
            config=default_config,
        )
        transaction_log = discography_subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="bandcamp/test_artist_url.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="bandcamp/test_artist_url.json",
        )

        # Ensure another invocation will hit ExistingVideoReached
        if not dry_run:
            with assert_logs(
                logger=YTDLP.logger,
                expected_message="ExistingVideoReached, stopping additional downloads",
                log_level="debug",
            ):
                transaction_log = discography_subscription.download()

            assert transaction_log.is_empty
            assert_expected_downloads(
                output_directory=output_directory,
                dry_run=dry_run,
                expected_download_summary_file_name="bandcamp/test_artist_url.json",
            )
