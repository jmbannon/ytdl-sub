import pytest

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def preset_dict_subscription_download_proba_0(output_directory):
    return {
        "preset": "Jellyfin Music Videos",
        "download": "https://youtube.com/watch?v=HKTNxEqsN3Q",
        "format": "worst[ext=mp4]",
        "overrides": {
            "music_video_artist": "JMC",
            "music_video_directory": output_directory,
        },
        "throttle_protection": {"subscription_download_probability": 0.0},
    }


class TestThrottleProtection:

    def test_subscription_probability(
        self,
        default_config,
        preset_dict_subscription_download_proba_0,
        output_directory,
    ):
        single_video_subscription = Subscription.from_dict(
            config=default_config,
            preset_name="music_video_single_video_test",
            preset_dict=preset_dict_subscription_download_proba_0,
        )

        transaction_log = single_video_subscription.download(dry_run=True)
        assert transaction_log.is_empty
