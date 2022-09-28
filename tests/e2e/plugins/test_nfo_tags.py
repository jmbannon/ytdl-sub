import pytest
from e2e.expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def subscription_dict(output_directory):
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
                "kodi_safe_title 🎸": "kodi_safe_value 🎸",
                "kodi_safe_title_with_attrs": {
                    "attributes": {"🎸?": "value\nnewlines 🎸"},
                    "tag": "the \n tag 🎸🎸",
                },
                "kodi_safe_multi_title 🎸": ["value 1 🎸", "value 2 🎸"],
                "kodi_safe_multi_title_with_attrs": [
                    {
                        "attributes": {"🎸?": "value\nnewlines 🎸"},
                        "tag": "the \n tag 1 🎸🎸",
                    },
                    {
                        "attributes": {"🎸?": "value\nnewlines 🎸"},
                        "tag": "the \n tag 2 🎸🎸",
                    },
                ],
            },
        },
        "output_directory_nfo_tags": {
            "nfo_name": "test.nfo",
            "nfo_root": "kodi_safe_root 🎸",
            "tags": {
                "kodi_safe_title 🎸": "kodi_safe_value 🎸",
                "kodi_safe_title_with_attrs": {
                    "attributes": {"🎸?": "value\nnewlines 🎸"},
                    "tag": "the \n tag 🎸🎸",
                },
                "kodi_safe_multi_title 🎸": ["value 1 🎸", "value 2 🎸"],
                "kodi_safe_multi_title_with_attrs": [
                    {
                        "attributes": {"🎸?": "value\nnewlines 🎸"},
                        "tag": "the \n tag 1 🎸🎸",
                    },
                    {
                        "attributes": {"🎸?": "value\nnewlines 🎸"},
                        "tag": "the \n tag 2 🎸🎸",
                    },
                ],
            },
        },
    }


@pytest.fixture
def merged_output_nfo_preset_dict(output_directory):
    return {
        "preset": "yt_music_video_playlist",
        "youtube": {"playlist_url": "https://youtube.com/playlist?list=PL5BC0FC26BECA5A35"},
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
        },
        "output_directory_nfo_tags": {
            "nfo_name": "tvshow.nfo",
            "nfo_root": "tvshow",
            "tags": {
                "title": "Test Title",
                "namedseason": [{"tag": "{title}", "attributes": {"number": "{playlist_index}"}}],
                "genre": [
                    "Comedy",
                    "Drama",
                ],
            },
        },
        "overrides": {"artist": "JMC"},
    }


class TestNfoTagsPlugins:
    @pytest.mark.parametrize("kodi_safe", [True, False])
    def test_nfo_tags(self, subscription_dict, music_video_config, output_directory, kodi_safe):
        transaction_log_file_name = "test_nfo.txt"
        if kodi_safe:
            transaction_log_file_name = "test_nfo_kodi_safe.txt"
            subscription_dict["nfo_tags"]["kodi_safe"] = True
            subscription_dict["output_directory_nfo_tags"]["kodi_safe"] = True

        subscription = Subscription.from_dict(
            config=music_video_config,
            preset_name="kodi_safe_xml",
            preset_dict=subscription_dict,
        )

        # Only dry run is needed to see if NFO values are kodi safe
        transaction_log = subscription.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"plugins/nfo_tags/{transaction_log_file_name}",
        )

    def test_merged_output_nfo_tags(
        self, merged_output_nfo_preset_dict, music_video_config, output_directory
    ):
        subscription = Subscription.from_dict(
            config=music_video_config,
            preset_name="merged_output_nfo_tags",
            preset_dict=merged_output_nfo_preset_dict,
        )

        # Only dry run is needed to see if NFO values are kodi safe
        transaction_log = subscription.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"plugins/nfo_tags/merged_output_nfo_tags.txt",
            regenerate_transaction_log=True,
        )
