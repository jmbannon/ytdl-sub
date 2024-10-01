import pytest
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def subscription_dict(output_directory):
    return {
        "preset": "Jellyfin Music Videos",
        "download": "https://your.name.here",
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        "format": "best[height<=480]",  # download the worst format so it is fast
        "nfo_tags": {
            "tags": {
                "kodi_safe_title 🎸": "kodi_safe_value 🎸",
                "kodi_safe_title_with_attrs": {
                    "attributes": {"🎸?": "value\nnewlines 🎸"},
                    "tag": "the \n tag 🎸🎸",
                },
                # should not show third empty
                "kodi_safe_multi_title 🎸": ["value 1 🎸", "value 2 🎸", ""],
                "kodi_safe_multi_title_with_attrs": [
                    {
                        "attributes": {"🎸?": "value\nnewlines 🎸"},
                        "tag": "the \n tag 1 🎸🎸",
                    },
                    {
                        "attributes": {"🎸?": "value\nnewlines 🎸"},
                        "tag": "the \n tag 2 🎸🎸",
                    },
                    {
                        "attributes": {"🎸?": "EMPTY TAG SHOULD NOT SHOW"},
                        "tag": "",
                    },
                ],
                "empty_attribute_tag_SHOULD_NOT_SHOW": {
                    "attributes": {"🎸?": "value\nnewlines 🎸"},
                    "tag": "",
                },
                "empty_tag_SHOULD_NOT_SHOW": "",
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
                # should not show third empty
                "kodi_safe_multi_title 🎸": ["value 1 🎸", "value 2 🎸", ""],
                "kodi_safe_multi_title_with_attrs": [
                    {
                        "attributes": {"🎸?": "value\nnewlines 🎸"},
                        "tag": "the \n tag 1 🎸🎸",
                    },
                    {
                        "attributes": {"🎸?": "value\nnewlines 🎸"},
                        "tag": "the \n tag 2 🎸🎸",
                    },
                    {
                        "attributes": {"🎸?": "EMPTY TAG SHOULD NOT SHOW"},
                        "tag": "",
                    },
                ],
                "empty_attribute_tag_SHOULD_NOT_SHOW": {
                    "attributes": {"🎸?": "value\nnewlines 🎸"},
                    "tag": "",
                },
                "empty_tag_SHOULD_NOT_SHOW": "",
            },
        },
    }


class TestNfoTagsPlugins:
    @pytest.mark.parametrize("kodi_safe", [True, False])
    def test_nfo_tags(
        self,
        subscription_name,
        subscription_dict,
        config,
        output_directory,
        mock_download_collection_entries,
        kodi_safe,
    ):
        transaction_log_file_name = "test_nfo.txt"
        if kodi_safe:
            transaction_log_file_name = "test_nfo_kodi_safe.txt"
            subscription_dict["nfo_tags"]["kodi_safe"] = True
            subscription_dict["output_directory_nfo_tags"]["kodi_safe"] = True

        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=subscription_dict,
        )

        # Only dry run is needed to see if NFO values are kodi safe
        with mock_download_collection_entries(
            is_youtube_channel=False, num_urls=1, is_extracted_audio=False
        ):
            transaction_log = subscription.download(dry_run=False)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"plugins/nfo_tags/{transaction_log_file_name}",
        )
