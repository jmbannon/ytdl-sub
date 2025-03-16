import pytest
from conftest import assert_logs
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def subscription_dict(output_directory):
    return {
        "preset": "SoundCloud Discography",
        "audio_extract": {"codec": "mp3", "quality": 320},
        "overrides": {
            "subscription_value": "https://soundcloud.com/jessebannon",
            "subscription_indent_1": "Acoustic",
            "music_directory": output_directory,
        },
    }


class TestSoundcloudDiscography:
    """
    Downloads my (bad) SC recordings I made. Ensure the above files exist and have the
    expected md5 file hashes.
    """

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_discography_download(
        self,
        subscription_dict,
        default_config,
        output_directory,
        dry_run,
    ):
        discography_subscription = Subscription.from_dict(
            preset_dict=subscription_dict,
            preset_name="j_b",
            config=default_config,
        )
        transaction_log = discography_subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="soundcloud/test_soundcloud_discography.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="soundcloud/test_soundcloud_discography.json",
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
                expected_download_summary_file_name="soundcloud/test_soundcloud_discography.json",
                ignore_md5_hashes_for=[
                    "j_b/[2021] Baby Santana's Dorian Groove/01 - Baby Santana's Dorian Groove.mp3",
                    "j_b/[2021] Purple Clouds/01 - Purple Clouds.mp3",
                    "j_b/[2022] Acoustic Treats/01 - 20160426 184214.mp3",
                    "j_b/[2022] Acoustic Treats/02 - 20160502 123150.mp3",
                    "j_b/[2022] Acoustic Treats/03 - 20160504 143832.mp3",
                    "j_b/[2022] Acoustic Treats/04 - 20160601 221234.mp3",
                    "j_b/[2022] Acoustic Treats/05 - 20160601 222440.mp3",
                    "j_b/[2022] Acoustic Treats/06 - 20170604 190236.mp3",
                    "j_b/[2022] Acoustic Treats/07 - 20170612 193646.mp3",
                    "j_b/[2022] Acoustic Treats/08 - 20170628 215206.mp3",
                    "j_b/[2022] Acoustic Treats/09 - Finding Home.mp3",
                    "j_b/[2022] Acoustic Treats/10 - Shallow Water WIP.mp3",
                    "j_b/[2022] Acoustic Treats/11 - Untold History.mp3",
                ]
            )
