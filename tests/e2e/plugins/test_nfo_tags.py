import pytest
from e2e.expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def kodi_safe_subscription_dict(output_directory):
    return {
        "preset": "yt_music_video",
        "youtube": {"video_url": "https://www.youtube.com/shorts/ucYmEqmlhFw"},
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "best[height<=480]",
        },
        "nfo_tags": {
            "tags": {
                "kodi_safe_title 🎸": "{title}",
            },
            "kodi_safe": True,
        },
        "output_directory_nfo_tags": {
            "nfo_name": "test.nfo",
            "nfo_root": "kodi_safe_root 🎸",
            "tags": {"kodi_safe_title 🎸": "kodi_safe_value 🎸"},
            "kodi_safe": True,
        },
    }


class TestNfoTagsPlugins:
    def test_kodi_safe(self, kodi_safe_subscription_dict, music_video_config, output_directory):
        subscription = Subscription.from_dict(
            config=music_video_config,
            preset_name="kodi_safe_xml",
            preset_dict=kodi_safe_subscription_dict,
        )

        # Only dry run is needed to see if NFO values are kodi safe
        transaction_log = subscription.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/test_kodi_safe_xml.txt",
            regenerate_transaction_log=True,
        )
