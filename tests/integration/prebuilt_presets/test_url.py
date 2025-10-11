import pytest
from conftest import assert_logs

from ytdl_sub.downloaders.url.downloader import MultiUrlDownloader
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions
from ytdl_sub.subscriptions.subscription import Subscription

v: VariableDefinitions = VARIABLES


@pytest.fixture
def subscription_dict(output_directory):
    return {
        "preset": [
            "Plex TV Show by Date",
            "Filter Keywords",
        ],
        "overrides": {
            "url": "https://your.name.here",
            "tv_show_directory": output_directory,
            "title_include_keywords": ["MOCK ENTRY 20-3"],
            "modified_webpage_url": "{webpage_url}_append_test",
        },
    }


class TestUrl:

    def test_modified_url_when_downloading(
        self,
        config,
        subscription_dict,
        subscription_name,
        working_directory,
    ):
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=subscription_dict,
        )

        assert set(
            url.webpage_url.format_string for url in subscription.downloader_options.urls.list
        ) == {"{modified_webpage_url}"}
        downloader = MultiUrlDownloader(
            options=subscription.downloader_options,
            enhanced_download_archive=subscription.download_archive,
            download_ytdl_options=YTDLOptionsBuilder(),
            metadata_ytdl_options=YTDLOptionsBuilder(),
            overrides=subscription.overrides,
        )

        entry = Entry(
            entry_dict={
                v.uid.metadata_key: "0",
                v.extractor.metadata_key: "test",
                v.extractor_key.metadata_key: "test",
                v.epoch.metadata_key: 123,
                v.webpage_url.metadata_key: "youtube.com/test_url",
                v.ext.metadata_key: "mp4",
            },
            working_directory=working_directory,
        )

        entry.initialize_base_script()

        entry.add_injected_variables(
            download_entry=entry,
            download_idx=0,
            upload_date_idx=0,
        ).initialize_script(subscription.overrides)

        entry.add({
            v.ytdl_sub_input_url_index.variable_name: 0
        })

        assert downloader.webpage_url(entry) == "youtube.com/test_url_append_test"
