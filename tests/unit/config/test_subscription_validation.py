import re

import pytest

from ytdl_sub.config.preset import Preset
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import StringFormattingVariableNotFoundException
from ytdl_sub.utils.exceptions import ValidationException


class TestSubscriptionValidation:
    def test_preset_error__source_variable_does_not_exist(
        self, config_file, output_options, youtube_video
    ):
        with pytest.raises(
            StringFormattingVariableNotFoundException,
            match="contains the following variables that do not exist: dne_var",
        ):
            _ = Subscription.from_preset(
                preset=Preset(
                    config=config_file,
                    name="test",
                    value={
                        "download": youtube_video,
                        "output_options": {"output_directory": "dir", "file_name": "{dne_var}"},
                    },
                ),
                config=config_file,
            )

    def test_preset_error__override_variable_does_not_exist(
        self, config_file, output_options, youtube_video
    ):
        with pytest.raises(
            StringFormattingVariableNotFoundException,
            match="contains the following variables that do not exist: dne_var",
        ):
            _ = Subscription.from_preset(
                preset=Preset(
                    config=config_file,
                    name="test",
                    value={
                        "download": youtube_video,
                        "output_options": {"output_directory": "{dne_var}", "file_name": "file"},
                    },
                ),
                config=config_file,
            )

    def test_preset_error__dict_source_variable_does_not_exist(
        self, config_file, output_options, youtube_video
    ):
        with pytest.raises(
            StringFormattingVariableNotFoundException,
            match="contains the following variables that do not exist: dne_var",
        ):
            _ = Subscription.from_preset(
                preset=Preset(
                    config=config_file,
                    name="test",
                    value={
                        "download": youtube_video,
                        "output_options": {"output_directory": "dir", "file_name": "file"},
                        "nfo_tags": {
                            "nfo_name": "the nfo name",
                            "nfo_root": "the root",
                            "tags": {"tag_a": "{dne_var}"},
                        },
                    },
                ),
                config=config_file,
            )

    def test_preset_error__dict_override_variable_does_not_exist(
        self, config_file, output_options, youtube_video
    ):
        with pytest.raises(
            StringFormattingVariableNotFoundException,
            match="contains the following variables that do not exist: dne_var",
        ):
            _ = Subscription.from_preset(
                preset=Preset(
                    config=config_file,
                    name="test",
                    value={
                        "download": youtube_video,
                        "output_options": output_options,
                        "output_directory_nfo_tags": {
                            "nfo_name": "the nfo name",
                            "nfo_root": "the root",
                            "tags": {"tag_a": "{dne_var}"},
                        },
                    },
                ),
                config=config_file,
            )

    def test_preset_error__dict_override_variable_not_static(
        self, config_file, output_options, youtube_video
    ):
        with pytest.raises(
            StringFormattingVariableNotFoundException,
            match="static formatters must contain variables that "
            "have no dependency to entry variables",
        ):
            _ = Subscription.from_preset(
                preset=Preset(
                    config=config_file,
                    name="test",
                    value={
                        "download": youtube_video,
                        "output_options": {
                            "output_directory": "{title}",
                            "file_name": "{uid}",
                        },
                    },
                ),
                config=config_file,
            )

    def test_preset_error_added_url_variable_cannot_resolve(self, config_file, output_options):
        with pytest.raises(
            ValidationException,
            match=re.escape(
                "variable the_bad_one cannot use the variables subtitles_ext because it "
                "depends on other variables that are computed later in execution"
            ),
        ):
            _ = Subscription.from_preset(
                preset=Preset(
                    config=config_file,
                    name="test",
                    value={
                        "download": {
                            "url": "youtube.com/watch?v=123abc",
                            "variables": {"the_bad_one": "{subtitles_ext}"},
                        },
                        "subtitles": {
                            "embed_subtitles": True,
                        },
                        "output_options": {"output_directory": "dir", "file_name": "acjk"},
                    },
                ),
                config=config_file,
            )
