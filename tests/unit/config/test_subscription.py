import re
from contextlib import contextmanager
from pathlib import Path
from typing import Dict
from unittest.mock import patch

import pytest
import yaml

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.validators.variable_validation import ResolutionLevel
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.plugins.nfo_tags import NfoTagsOptions
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.script import ScriptUtils


@contextmanager
def mock_load_yaml(preset_dict: Dict) -> None:
    with patch("ytdl_sub.subscriptions.subscription.load_yaml") as mock_load_yaml:
        mock_load_yaml.return_value = preset_dict
        yield


@pytest.fixture
def preset_with_file_preset(youtube_video: Dict, output_options: Dict):
    return {
        "__preset__": {
            "download": youtube_video,
            "output_options": output_options,
            "nfo_tags": {
                "nfo_name": "eh",
                "nfo_root": "eh",
                "tags": {"key-3": "file_preset"},
            },
            "overrides": {
                "subscription_indent_1": "original_1",
                "subscription_indent_2": "original_2",
                "current_override": "__preset__",
            },
        },
        "test_preset": {
            "preset": "parent_preset_3",
            "nfo_tags": {
                "tags": {"key-4": "test_preset"},
            },
            "overrides": {"current_override": "test_preset"},
        },
    }


@pytest.fixture
def preset_with_subscription_value(preset_with_file_preset: Dict):
    return dict(
        preset_with_file_preset,
        **{
            "test_value": "is_overwritten",
        },
    )


@pytest.fixture
def subscription_with_period_in_name(preset_with_file_preset: Dict):
    return dict(
        preset_with_file_preset,
        **{
            "Mr. Beast": "is_overwritten",
        },
    )


@pytest.fixture
def preset_with_subscription_value_nested_presets(preset_with_subscription_value: Dict):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2": {
                "parent_preset_1": {"test_2_1": "is_2_1_overwritten"},
                "test_1": "is_1_overwritten",
            }
        },
    )


@pytest.fixture
def preset_with_subscription_value_nested_presets_and_indent_variables(
    preset_with_subscription_value: Dict,
):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2": {
                "= INDENT_1   ": {
                    "parent_preset_1": {"test_2_1": "is_2_1_overwritten"},
                    "=INDENT_2": {
                        "test_1": "is_1_overwritten",
                    },
                }
            }
        },
    )


@pytest.fixture
def preset_with_subscription_value_nested_presets_and_indent_variables_same_line(
    preset_with_subscription_value: Dict,
):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2": {
                "=INDENT_1": {
                    "parent_preset_1": {"test_2_1": "is_2_1_overwritten"},
                    "= INDENT_2  | = INDENT_3   ": {
                        "test_1": "is_1_overwritten",
                    },
                }
            }
        },
    )


@pytest.fixture
def preset_with_subscription_value_nested_presets_and_indent_variables_all_same_line(
    preset_with_subscription_value: Dict,
):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2 | =INDENT_1 | parent_preset_1": {
                "test_2_1": "is_2_1_overwritten",
            },
            "parent_preset_2 | =INDENT_1 |= INDENT_2  | = INDENT_3   ": {
                "test_1": "is_1_overwritten",
            },
        },
    )


@pytest.fixture
def preset_with_subscription_list(
    preset_with_subscription_value: Dict,
):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2 | parent_preset_1": {
                "test_2_1": ["is_2_1_overwritten", "is_2_1_list_2"]
            },
        },
    )


@pytest.fixture
def preset_with_subscription_overrides_tilda(
    preset_with_subscription_value: Dict,
):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2 | parent_preset_1": {
                "~ test_2_1": {
                    "current_override": "test_2_1",
                    "custom_list": [
                        "elem1",
                        "elem2",
                        "elem3",
                    ],
                    "passed_list_elem": "{%contains_any('elem2', custom_list)}",
                }
            },
        },
    )


@pytest.fixture
def preset_with_subscription_overrides_map(
    preset_with_subscription_value: Dict,
):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2 | parent_preset_1": {
                "+ test_2_1": {
                    "custom_key": "custom_value",
                    "custom_list": [
                        "elem1",
                        "elem2",
                        "elem3",
                    ],
                    "custom_map": {"custom_map_key": ["custom_map_list_value"]},
                }
            },
        },
    )


@pytest.fixture
def preset_with_subscription_value_nested_presets_and_indent_variables_same_line_old_format_errors(
    preset_with_subscription_value: Dict,
):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2": {
                "=INDENT_1": {
                    "parent_preset_1": {"test_2_1": "is_2_1_overwritten"},
                    "= INDENT_2  | INDENT_3   ": {
                        "test_1": "is_1_overwritten",
                    },
                }
            }
        },
    )


def test_subscription_file_preset_applies(config_file: ConfigFile, preset_with_file_preset: Dict):
    with mock_load_yaml(preset_dict=preset_with_file_preset):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 1

    # Test __preset__ worked correctly
    preset_sub = subs[0]
    assert preset_sub.name == "test_preset"

    nfo_options: NfoTagsOptions = preset_sub.plugins.get(NfoTagsOptions)
    tags_string_dict = {
        key: formatter[0].format_string for key, formatter in nfo_options.tags.string_tags.items()
    }

    assert tags_string_dict == {
        "key-1": "preset_0",
        "key-2": "preset_2",
        "key-3": "file_preset",
        "key-4": "test_preset",
    }

    overrides = preset_sub.overrides.script
    # preset overrides take precedence over __preset__
    assert overrides.get("current_override").native == "test_preset"


def test_subscription_list(
    config_file: ConfigFile,
    preset_with_subscription_list: Dict,
):
    with mock_load_yaml(preset_dict=preset_with_subscription_list):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 3

    sub_2_1 = [sub for sub in subs if sub.name == "test_2_1"][0].overrides.script

    assert sub_2_1.get("subscription_name").native == "test_2_1"
    assert sub_2_1.get("subscription_value").native == "is_2_1_overwritten"
    assert sub_2_1.get("subscription_value_1").native == "is_2_1_overwritten"
    assert sub_2_1.get("subscription_value_2").native == "is_2_1_list_2"
    assert (
        sub_2_1.get("current_override").native == "__preset__"
    )  # ensure __preset__ takes precedence


def test_subscription_overrides_tilda(
    config_file: ConfigFile,
    preset_with_subscription_overrides_tilda: Dict,
):
    with mock_load_yaml(preset_dict=preset_with_subscription_overrides_tilda):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 3

    sub_2_1 = [sub for sub in subs if sub.name == "test_2_1"][0].overrides.script

    assert sub_2_1.get("subscription_name").native == "test_2_1"
    assert sub_2_1.get("current_override").native == "test_2_1"  # tilda sub takes precedence
    assert sub_2_1.get("passed_list_elem").native is True
    assert sub_2_1.get("custom_list").native == ["elem1", "elem2", "elem3"]


def test_subscription_overrides_map(
    config_file: ConfigFile,
    preset_with_subscription_overrides_map: Dict,
):
    with mock_load_yaml(preset_dict=preset_with_subscription_overrides_map):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 3

    sub_2_1 = [sub for sub in subs if sub.name == "test_2_1"][0].overrides.script

    assert sub_2_1.get("subscription_name").native == "test_2_1"
    assert sub_2_1.get("subscription_map").native == {
        "custom_key": "custom_value",
        "custom_list": [
            "elem1",
            "elem2",
            "elem3",
        ],
        "custom_map": {"custom_map_key": ["custom_map_list_value"]},
    }


def test_subscription_with_period_in_name(
    config_file: ConfigFile,
    subscription_with_period_in_name: Dict,
):
    with mock_load_yaml(preset_dict=subscription_with_period_in_name):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 2

    assert subs[1].name == "Mr. Beast"
    assert subs[1].overrides.script.get("subscription_name").native == "Mr. Beast"


def test_subscription_file_value_applies_from_config_and_nested_and_indent_variables(
    config_file: ConfigFile,
    preset_with_subscription_value_nested_presets_and_indent_variables: Dict,
):
    with mock_load_yaml(
        preset_dict=preset_with_subscription_value_nested_presets_and_indent_variables
    ):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 4

    sub_test_value = [sub for sub in subs if sub.name == "test_value"][0].overrides.script
    sub_1 = [sub for sub in subs if sub.name == "test_1"][0].overrides.script
    sub_2_1 = [sub for sub in subs if sub.name == "test_2_1"][0].overrides.script

    assert sub_test_value.get("subscription_indent_1").native == "original_1"
    assert sub_test_value.get("subscription_indent_2").native == "original_2"

    assert sub_1.get("subscription_name").native == "test_1"
    assert sub_1.get("subscription_value").native == "is_1_overwritten"
    assert sub_1.get("subscription_indent_1").native == "INDENT_1"
    assert sub_1.get("subscription_indent_2").native == "INDENT_2"
    assert (
        sub_1.get("current_override").native == "__preset__"
    )  # ensure __preset__ takes precedence

    assert sub_2_1.get("subscription_name").native == "test_2_1"
    assert sub_2_1.get("subscription_value").native == "is_2_1_overwritten"
    assert sub_2_1.get("subscription_indent_1").native == "INDENT_1"
    assert sub_2_1.get("subscription_indent_2").native == "original_2"
    assert (
        sub_2_1.get("current_override").native == "__preset__"
    )  # ensure __preset__ takes precedence


@pytest.mark.parametrize("all_same_line", [True, False])
def test_subscription_file_value_applies_from_config_and_nested_and_indent_variables_same_line(
    config_file: ConfigFile,
    preset_with_subscription_value_nested_presets_and_indent_variables_same_line: Dict,
    preset_with_subscription_value_nested_presets_and_indent_variables_all_same_line: Dict,
    all_same_line: bool,
):
    preset_dict = preset_with_subscription_value_nested_presets_and_indent_variables_same_line
    if all_same_line:
        preset_dict = (
            preset_with_subscription_value_nested_presets_and_indent_variables_all_same_line
        )

    with mock_load_yaml(preset_dict=preset_dict):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 4

    sub_test_value = [sub for sub in subs if sub.name == "test_value"][0].overrides.script
    sub_1 = [sub for sub in subs if sub.name == "test_1"][0].overrides.script
    sub_2_1 = [sub for sub in subs if sub.name == "test_2_1"][0].overrides.script

    assert sub_test_value.get("subscription_indent_1").native == "original_1"
    assert sub_test_value.get("subscription_indent_2").native == "original_2"

    assert sub_1.get("subscription_name").native == "test_1"
    assert sub_1.get("subscription_value").native == "is_1_overwritten"
    assert sub_1.get("subscription_indent_1").native == "INDENT_1"
    assert sub_1.get("subscription_indent_2").native == "INDENT_2"
    assert sub_1.get("subscription_indent_3").native == "INDENT_3"
    # ensure __preset__ takes precedence
    assert sub_1.get("current_override").native == "__preset__"

    assert sub_2_1.get("subscription_name").native == "test_2_1"
    assert sub_2_1.get("subscription_value").native == "is_2_1_overwritten"
    assert sub_2_1.get("subscription_indent_1").native == "INDENT_1"
    assert sub_2_1.get("subscription_indent_2").native == "original_2"
    # ensure __preset__ takes precedence
    assert sub_2_1.get("current_override").native == "__preset__"
    assert "subscription_indent_3" not in sub_2_1.variable_names


def test_subscription_file_value_applies_from_config_and_nested_and_indent_variables_same_line_old_format_errors(
    config_file: ConfigFile,
    preset_with_subscription_value_nested_presets_and_indent_variables_same_line_old_format_errors: Dict,
):
    with (
        mock_load_yaml(
            preset_dict=preset_with_subscription_value_nested_presets_and_indent_variables_same_line_old_format_errors
        ),
        pytest.raises(
            ValidationException,
            match=re.escape(
                "Validation error in parent_preset_2.=INDENT_1: 'INDENT_3' in '= INDENT_2  | INDENT_3' is not a preset name. "
                "To use as a subscription indent value, define it as '= INDENT_3'"
            ),
        ),
    ):
        Subscription.from_file_path(config=config_file, subscription_path="mocked")


def test_subscription_file_using_conflicting_preset_name(config_file: ConfigFile):
    with (
        mock_load_yaml(
            preset_dict={
                "= INDENTS_IN_ERR_MSG ": {"=ANOTHER": {"jellyfin_tv_show_by_date": "single value"}}
            }
        ),
        pytest.raises(
            ValidationException,
            match=re.escape(
                "Validation error in = INDENTS_IN_ERR_MSG .=ANOTHER.jellyfin_tv_show_by_date: "
                "jellyfin_tv_show_by_date conflicts with an existing preset name and cannot be used "
                "as a subscription name"
            ),
        ),
    ):
        _ = Subscription.from_file_path(config=config_file, subscription_path="mocked")


def test_subscription_file_invalid_form(config_file: ConfigFile):
    with (
        mock_load_yaml(preset_dict={"sub_name": 4332}),
        pytest.raises(
            ValidationException,
            match=re.escape(f"Subscription value should either be a string, list, or object"),
        ),
    ):
        _ = Subscription.from_file_path(config=config_file, subscription_path="mocked")


def test_tv_show_subscriptions(config_file: ConfigFile, tv_show_subscriptions_path: Path):
    subs = Subscription.from_file_path(
        config=config_file, subscription_path=tv_show_subscriptions_path
    )

    assert len(subs) == 8
    assert subs[3].name == "Jake Trains"
    jake_train_overrides = subs[3].overrides.script

    assert jake_train_overrides.get("subscription_name").native == "Jake Trains"
    assert (
        jake_train_overrides.get("subscription_value").native
        == "https://www.youtube.com/@JakeTrains"
    )
    assert jake_train_overrides.get("subscription_indent_1").native == "Kids"
    assert jake_train_overrides.get("subscription_indent_2").native == "TV-Y"


def test_advanced_tv_show_subscriptions(
    tv_show_config: ConfigFile, advanced_tv_show_subscriptions_path: Path
):
    subs = Subscription.from_file_path(
        config=tv_show_config, subscription_path=advanced_tv_show_subscriptions_path
    )

    assert len(subs) == 9
    assert subs[3].name == "Jake Trains"
    jake_train_overrides = subs[3].overrides.script

    assert jake_train_overrides.get("subscription_name").native == "Jake Trains"
    assert (
        jake_train_overrides.get("subscription_value").native
        == "https://www.youtube.com/@JakeTrains"
    )
    assert jake_train_overrides.get("subscription_indent_1").native == "Kids"
    assert jake_train_overrides.get("subscription_indent_2").native == "TV-Y"

    assert subs[5].name == "Gardening with Ciscoe"
    overrides = subs[5].overrides

    assert overrides.script.get("subscription_name").native == "Gardening with Ciscoe"

    assert overrides.apply_overrides_formatter_to_native(overrides.dict["subscription_array"]) == [
        "https://www.youtube.com/@gardeningwithciscoe4430",
        "https://www.youtube.com/playlist?list=PLi8V8UemxeG6lo5if5H5g5EbsteELcb0_",
        "https://www.youtube.com/playlist?list=PLsJlQSR-KjmaQqqJ9jq18cF6XXXAR4kyn",
        "https://www.youtube.com/watch?v=2vq-vPubS5I",
    ]
    assert overrides.apply_overrides_formatter_to_native(overrides.dict["urls"]) == [
        "https://www.youtube.com/@gardeningwithciscoe4430",
        "https://www.youtube.com/playlist?list=PLi8V8UemxeG6lo5if5H5g5EbsteELcb0_",
        "https://www.youtube.com/playlist?list=PLsJlQSR-KjmaQqqJ9jq18cF6XXXAR4kyn",
        "https://www.youtube.com/watch?v=2vq-vPubS5I",
    ]


def test_music_subscriptions(default_config: ConfigFile, music_subscriptions_path: Path):
    subs = Subscription.from_file_path(
        config=default_config, subscription_path=music_subscriptions_path
    )

    assert len(subs) == 14
    assert subs[2].name == "Stan Getz"
    monk = subs[2].overrides.script

    assert monk.get("subscription_name").native == "Stan Getz"
    assert (
        monk.get("subscription_value").native
        == "https://www.youtube.com/@stangetzofficial/releases"
    )
    assert monk.get("subscription_indent_1").native == "Jazz"


def test_music_video_subscriptions(default_config: ConfigFile, music_video_subscription_path: Path):
    subs = Subscription.from_file_path(
        config=default_config, subscription_path=music_video_subscription_path
    )

    assert len(subs) == 4
    assert subs[1].name == "Michael Jackson"
    jackson = subs[1].overrides.script

    assert jackson.get("subscription_name").native == "Michael Jackson"
    assert (
        jackson.get("subscription_value").native
        == "https://www.youtube.com/playlist?list=OLAK5uy_mnY03zP6abNWH929q2XhGzWD_2uKJ_n8E"
    )
    assert jackson.get("subscription_indent_1").native == "Pop"
    assert (
        jackson.get("urls").native[0]
        == "https://www.youtube.com/playlist?list=OLAK5uy_mnY03zP6abNWH929q2XhGzWD_2uKJ_n8E"
    )

    assert subs[3].name == "Guns N' Roses"
    gnr = subs[3].overrides.script

    assert gnr.get("subscription_name").native == "Guns N' Roses"
    gnr_urls = gnr.get("urls").native
    assert gnr_urls[0] == "https://www.youtube.com/playlist?list=PLOTK54q5K4INNXaHKtmXYr6J7CajWjqeJ"
    assert gnr.get("subscription_indent_1").native == "Rock"
    assert gnr_urls[1] == "https://www.youtube.com/watch?v=OldpIhHPsbs"


def test_default_docker_config_and_subscriptions(
    docker_default_subscription_path: Path, output_directory: str
):
    default_config = ConfigFile.from_file_path("docker/root/defaults/config.yaml")
    default_subs = Subscription.from_file_path(
        config=default_config, subscription_path=docker_default_subscription_path
    )
    assert len(default_subs) == 1

    resolved_yaml_as_json = yaml.safe_load(default_subs[0].resolved_yaml())

    assert resolved_yaml_as_json == {
        "chapters": {
            "allow_chapters_from_comments": False,
            "embed_chapters": True,
            "enable": "True",
            "force_key_frames": False,
        },
        "date_range": {"breaks": "True", "enable": "True", "type": "upload_date"},
        "download": [
            {
                "download_reverse": "True",
                "include_sibling_metadata": False,
                "playlist_thumbnails": [
                    {"name": "{avatar_uncropped_thumbnail_file_name}", "uid": "avatar_uncropped"},
                    {"name": "{banner_uncropped_thumbnail_file_name}", "uid": "banner_uncropped"},
                ],
                "source_thumbnails": [
                    {"name": "{avatar_uncropped_thumbnail_file_name}", "uid": "avatar_uncropped"},
                    {"name": "{banner_uncropped_thumbnail_file_name}", "uid": "banner_uncropped"},
                ],
                "url": "https://www.youtube.com/@novapbs",
                "variables": {},
                "webpage_url": "{modified_webpage_url}",
                "ytdl_options": {},
            }
        ],
        "file_convert": {"convert_to": "mp4", "convert_with": "yt-dlp", "enable": "True"},
        "format": "(bv*[ext=mp4][vcodec~='^((he|a)vc|h26[45])']+ba[ext=m4a]) / (bv[ext=mp4]*+ba[ext=m4a]/b)",
        "output_options": {
            "download_archive_name": ".ytdl-sub-NOVA PBS-download-archive.json",
            "file_name": "{episode_file_path}.{ext}",
            "info_json_name": "{episode_file_path}.{info_json_ext}",
            "keep_files_date_eval": "{episode_date_standardized}",
            "maintain_download_archive": True,
            "output_directory": f"{output_directory}/NOVA PBS",
            "preserve_mtime": False,
            "thumbnail_name": "{thumbnail_file_name}",
        },
        'overrides': {'%bilateral_url': '{ %if( %and( enable_bilateral_scraping, '
                                        'subscription_has_download_archive, '
                                        "%is_bilateral_url( $0 ) ), $0, '' ) }",
                      '%episode_ordering_': '{ %eq( %lower( '
                                            'tv_show_by_date_episode_ordering ), $0 ) '
                                            '}',
                      '%is_bilateral_url': '{ %contains( $0, "youtube.com/playlist" ) '
                                           '}',
                      '%ordering_pair_eq': '{ %eq( [ tv_show_by_date_season_ordering, '
                                           'tv_show_by_date_episode_ordering ], [ $0, '
                                           '$1 ] ) }',
                      '%season_ordering_': '{ %eq( %lower( '
                                           'tv_show_by_date_season_ordering ), $0 ) }',
                      'assert_not_collection': '{ %assert( %and( %not( %bool( s01_url '
                                               ') ), %not( %bool( s01_name ) ) ), '
                                               '"Provided `s01_url` or `s01_name` '
                                               'variable to TV Show by Date preset '
                                               'when it expects `url`. Perhaps you '
                                               'meant to use the `TV Show Collection` '
                                               'preset?" ) }',
                      'avatar_uncropped_thumbnail_file_name': '{ '
                                                              'tv_show_poster_file_name '
                                                              '}',
                      'banner_uncropped_thumbnail_file_name': '{ '
                                                              'tv_show_fanart_file_name '
                                                              '}',
                      'enable_bilateral_scraping': '{ %bool(True) }',
                      'enable_resolution_assert': '{ %bool(True) }',
                      'enable_throttle_protection': '{ %bool(True) }',
                      'episode_content_rating': '{ tv_show_content_rating }',
                      'episode_date_standardized': '{ %if( %contains( '
                                                   'tv_show_by_date_season_ordering, '
                                                   '"release" ), '
                                                   'release_date_standardized, '
                                                   'upload_date_standardized ) }',
                      'episode_file_name': '{ %concat( %string( "s" ), %string( '
                                           'season_number_padded ), %string( ".e" ), '
                                           '%string( episode_number_padded ), '
                                           '%string( " - " ), %string( file_title ) ) '
                                           '}',
                      'episode_file_path': '{ %concat( %string( '
                                           'season_directory_name_sanitized ), '
                                           '%string( "/" ), %string( '
                                           'episode_file_name_sanitized ) ) }',
                      'episode_number': '{ %array_at( episode_number_and_padded_, 0 ) '
                                        '}',
                      'episode_number_and_padded_': '{ %elif( %episode_ordering_( '
                                                    '"upload-day" ), [ %concat( '
                                                    'upload_day, '
                                                    'upload_date_index_padded ), 4 ], '
                                                    '%episode_ordering_( '
                                                    '"upload-month-day" ), [ %concat( '
                                                    'upload_month, upload_day_padded, '
                                                    'upload_date_index_padded ), 6 ], '
                                                    '%episode_ordering_( '
                                                    '"upload-month-day-reversed" ), [ '
                                                    '%concat( '
                                                    'upload_day_of_year_reversed, '
                                                    'upload_date_index_reversed_padded '
                                                    '), 5 ], %episode_ordering_( '
                                                    '"release-day" ), [ %concat( '
                                                    'release_day, '
                                                    'upload_date_index_padded ), 4 ], '
                                                    '%episode_ordering_( '
                                                    '"release-month-day" ), [ '
                                                    '%concat( release_month, '
                                                    'release_day_padded, '
                                                    'upload_date_index_padded ), 6 ], '
                                                    '%episode_ordering_( '
                                                    '"release-month-day-reversed" ), '
                                                    '[ %concat( '
                                                    'release_day_of_year_reversed, '
                                                    'upload_date_index_reversed_padded '
                                                    '), 5 ], %episode_ordering_( '
                                                    '"download-index" ), [ '
                                                    'download_index, 6 ], %throw( '
                                                    "'tv_show_by_date_episode_ordering "
                                                    'must be one of the following: '
                                                    '"upload-day", '
                                                    '"upload-month-day", '
                                                    '"upload-month-day-reversed", '
                                                    '"release-day", '
                                                    '"release-month-day", '
                                                    '"release-month-day-reversed", '
                                                    '"download-index"\' ) ) }',
                      'episode_number_padded': '{ %pad_zero( %int( episode_number ), '
                                               '%int( %array_at( '
                                               'episode_number_and_padded_, 1 ) ) ) }',
                      'episode_plot': '{ %concat( %string( webpage_url ), %string( "\n'
                                      '\n'
                                      '" ), %string( description ) ) }',
                      'episode_title': '{ %concat( %string( episode_date_standardized '
                                       '), %string( " - " ), %string( title ) ) }',
                      'episode_year': '{ %slice( episode_date_standardized, 0, 4 ) }',
                      'file_title': '{ title_sanitized_plex }',
                      'file_uid': '{ uid_sanitized_plex }',
                      'include_sibling_metadata': '{ %bool(False) }',
                      'modified_webpage_url': '{ webpage_url }',
                      'music_directory': '/music',
                      'music_video_directory': '/music_videos',
                      'resolution_assert': '{ %if( %and( enable_resolution_assert, '
                                           '%ne( height, 0 ), %not( '
                                           'resolution_assert_is_ignored ) ), '
                                           '%assert( %gte( height, '
                                           'resolution_assert_height_gte ), %concat( '
                                           '"Entry ", title, " downloaded at a low '
                                           'resolution (", resolution_readable, "), '
                                           'you\'ve probably been throttled. ", '
                                           '"Stopping further downloads, wait a few '
                                           'hours and try again. ", "Disable using '
                                           'the override variable '
                                           '`enable_resolution_assert: False`." ) ), '
                                           '"false is no-op" ) }',
                      'resolution_assert_height_gte': '{ %int(361) }',
                      'resolution_assert_ignore_titles': '{ [  ] }',
                      'resolution_assert_is_ignored': '{ %print_if_true( %concat( '
                                                      'title, " has a match in '
                                                      'resolution_assert_ignore_titles, '
                                                      'skipping resolution assert." '
                                                      '), %contains_any( title, '
                                                      'resolution_assert_ignore_titles '
                                                      ') ) }',
                      'resolution_assert_print': '{ %print( %if( '
                                                 'enable_resolution_assert, '
                                                 '"Resolution assert is enabled, will '
                                                 'fail on low-quality video downloads '
                                                 'and presume throttle. Disable using '
                                                 'the override variable '
                                                 '`enable_resolution_assert: False`", '
                                                 '"Resolution assert is disabled. Use '
                                                 'at your own risk!" ), '
                                                 'enable_resolution_assert, -1 ) }',
                      'resolution_readable': '{ %concat( %string( width ), %string( '
                                             '"x" ), %string( height ) ) }',
                      's01_name': '',
                      's01_url': '',
                      'season_directory_name': '{ %concat( %string( "Season " ), '
                                               '%string( season_number_padded ) ) }',
                      'season_number': '{ %elif( %season_ordering_( "upload-year" ), '
                                       'upload_year, %season_ordering_( '
                                       '"upload-year-month" ), %concat( upload_year, '
                                       'upload_month_padded ), %season_ordering_( '
                                       '"release-year" ), release_year, '
                                       '%season_ordering_( "release-year-month" ), '
                                       '%concat( release_year, release_month_padded '
                                       "), %throw( 'tv_show_by_date_season_ordering "
                                       'must be one of the following: "upload-year", '
                                       '"upload-year-month", "release-year", '
                                       '"release-year-month"\' ) ) }',
                      'season_number_padded': '{ season_number }',
                      'season_poster_file_name': '{ %concat( %string( '
                                                 'season_directory_name_sanitized ), '
                                                 '%string( "/Season" ), %string( '
                                                 'season_number_padded ), %string( '
                                                 '".jpg" ) ) }',
                      'subscription_array': '{ %from_json( '
                                            '\'["https://www.youtube.com/@novapbs"]\' '
                                            ') }',
                      'subscription_indent_1': 'Documentaries',
                      'subscription_indent_2': '{ tv_show_content_rating_default }',
                      'subscription_value': 'https://www.youtube.com/@novapbs',
                      'subscription_value_1': 'https://www.youtube.com/@novapbs',
                      'thumbnail_file_name': '{ %concat( %string( episode_file_path '
                                             '), %string( "-thumb.jpg" ) ) }',
                      'tv_show_by_date_episode_ordering': 'upload-month-day',
                      'tv_show_by_date_ordering_pair_validation_': '{ %assert_then( '
                                                                   '%or( '
                                                                   '%ordering_pair_eq( '
                                                                   '"upload-year", '
                                                                   '"upload-month-day" '
                                                                   '), '
                                                                   '%ordering_pair_eq( '
                                                                   '"upload-year", '
                                                                   '"upload-month-day-reversed" '
                                                                   '), '
                                                                   '%ordering_pair_eq( '
                                                                   '"upload-year", '
                                                                   '"download-index" '
                                                                   '), '
                                                                   '%ordering_pair_eq( '
                                                                   '"upload-year-month", '
                                                                   '"upload-day" ), '
                                                                   '%ordering_pair_eq( '
                                                                   '"release-year", '
                                                                   '"release-month-day" '
                                                                   '), '
                                                                   '%ordering_pair_eq( '
                                                                   '"release-year", '
                                                                   '"release-month-day-reversed" '
                                                                   '), '
                                                                   '%ordering_pair_eq( '
                                                                   '"release-year", '
                                                                   '"download-index" '
                                                                   '), '
                                                                   '%ordering_pair_eq( '
                                                                   '"release-year-month", '
                                                                   '"release-day" ) '
                                                                   '), '
                                                                   'episode_number_and_padded_, '
                                                                   '"Detected '
                                                                   'incompatibility '
                                                                   'between '
                                                                   'tv_show_by_date_season_ordering '
                                                                   'and '
                                                                   'tv_show_by_date_episode_ordering. '
                                                                   'Ensure you are '
                                                                   'not using both '
                                                                   'upload and '
                                                                   'release date, and '
                                                                   'that the '
                                                                   'year/month/day '
                                                                   'are included in '
                                                                   'the combined '
                                                                   'season and '
                                                                   'episode." ) }',
                      'tv_show_by_date_season_ordering': 'upload-year',
                      'tv_show_content_rating': '{ subscription_indent_2 }',
                      'tv_show_content_rating_default': 'TV-14',
                      'tv_show_date_range_type': '{ %if( %contains( '
                                                 'tv_show_by_date_season_ordering, '
                                                 '"release" ), "release_date", '
                                                 '"upload_date" ) }',
                      'tv_show_directory': output_directory,
                      'tv_show_fanart_file_name': 'fanart.jpg',
                      'tv_show_genre': '{ subscription_indent_1 }',
                      'tv_show_genre_default': 'ytdl-sub',
                      'tv_show_name': '{ subscription_name }',
                      'tv_show_poster_file_name': 'poster.jpg',
                      'url': '{ subscription_value }',
                      'url10': '',
                      'url100': '',
                      'url11': '',
                      'url12': '',
                      'url13': '',
                      'url14': '',
                      'url15': '',
                      'url16': '',
                      'url17': '',
                      'url18': '',
                      'url19': '',
                      'url2': '',
                      'url20': '',
                      'url21': '',
                      'url22': '',
                      'url23': '',
                      'url24': '',
                      'url25': '',
                      'url26': '',
                      'url27': '',
                      'url28': '',
                      'url29': '',
                      'url3': '',
                      'url30': '',
                      'url31': '',
                      'url32': '',
                      'url33': '',
                      'url34': '',
                      'url35': '',
                      'url36': '',
                      'url37': '',
                      'url38': '',
                      'url39': '',
                      'url4': '',
                      'url40': '',
                      'url41': '',
                      'url42': '',
                      'url43': '',
                      'url44': '',
                      'url45': '',
                      'url46': '',
                      'url47': '',
                      'url48': '',
                      'url49': '',
                      'url5': '',
                      'url50': '',
                      'url51': '',
                      'url52': '',
                      'url53': '',
                      'url54': '',
                      'url55': '',
                      'url56': '',
                      'url57': '',
                      'url58': '',
                      'url59': '',
                      'url6': '',
                      'url60': '',
                      'url61': '',
                      'url62': '',
                      'url63': '',
                      'url64': '',
                      'url65': '',
                      'url66': '',
                      'url67': '',
                      'url68': '',
                      'url69': '',
                      'url7': '',
                      'url70': '',
                      'url71': '',
                      'url72': '',
                      'url73': '',
                      'url74': '',
                      'url75': '',
                      'url76': '',
                      'url77': '',
                      'url78': '',
                      'url79': '',
                      'url8': '',
                      'url80': '',
                      'url81': '',
                      'url82': '',
                      'url83': '',
                      'url84': '',
                      'url85': '',
                      'url86': '',
                      'url87': '',
                      'url88': '',
                      'url89': '',
                      'url9': '',
                      'url90': '',
                      'url91': '',
                      'url92': '',
                      'url93': '',
                      'url94': '',
                      'url95': '',
                      'url96': '',
                      'url97': '',
                      'url98': '',
                      'url99': '',
                      'urls': '{ subscription_array }'},
        "throttle_protection": {
            "enable": True,
            "sleep_per_download_s": {"max": "28.4", "min": "13.8"},
            "sleep_per_request_s": {"max": "0.75", "min": "0.0"},
            "sleep_per_subscription_s": {"max": "26.1", "min": "16.3"},
        },
        "video_tags": {
            "contentRating": "{episode_content_rating}",
            "date": "{episode_date_standardized}",
            "episode_id": "{episode_number}",
            "genre": "{tv_show_genre}",
            "show": "{tv_show_name}",
            "synopsis": "{episode_plot}",
            "title": "{episode_title}",
            "year": "{episode_year}",
        },
    }


def test_default_docker_config_and_subscriptions_resolved_resolution(
    docker_default_subscription_path: Path, output_directory: str
):
    default_config = ConfigFile.from_file_path("docker/root/defaults/config.yaml")
    default_subs = Subscription.from_file_path(
        config=default_config, subscription_path=docker_default_subscription_path
    )
    assert len(default_subs) == 1

    resolved_yaml_as_json = yaml.safe_load(default_subs[0].resolved_yaml(resolution_level=ResolutionLevel.RESOLVE))

    assert resolved_yaml_as_json == {
        "chapters": {
            "allow_chapters_from_comments": False,
            "embed_chapters": True,
            "enable": "True",
            "force_key_frames": False,
        },
        "date_range": {"breaks": "True", "enable": "True", "type": "upload_date"},
        "download": [
            {
                "download_reverse": "True",
                "include_sibling_metadata": False,
                "playlist_thumbnails": [
                    {"name": "{avatar_uncropped_thumbnail_file_name}", "uid": "avatar_uncropped"},
                    {"name": "{banner_uncropped_thumbnail_file_name}", "uid": "banner_uncropped"},
                ],
                "source_thumbnails": [
                    {"name": "{avatar_uncropped_thumbnail_file_name}", "uid": "avatar_uncropped"},
                    {"name": "{banner_uncropped_thumbnail_file_name}", "uid": "banner_uncropped"},
                ],
                "url": "https://www.youtube.com/@novapbs",
                "variables": {},
                "webpage_url": "{modified_webpage_url}",
                "ytdl_options": {},
            }
        ],
        "file_convert": {"convert_to": "mp4", "convert_with": "yt-dlp", "enable": "True"},
        "format": "(bv*[ext=mp4][vcodec~='^((he|a)vc|h26[45])']+ba[ext=m4a]) / (bv[ext=mp4]*+ba[ext=m4a]/b)",
        "output_options": {
            "download_archive_name": ".ytdl-sub-NOVA PBS-download-archive.json",
            "file_name": "{episode_file_path}.{ext}",
            "info_json_name": "{episode_file_path}.{info_json_ext}",
            "keep_files_date_eval": "{episode_date_standardized}",
            "maintain_download_archive": True,
            "output_directory": f"{output_directory}/NOVA PBS",
            "preserve_mtime": False,
            "thumbnail_name": "{thumbnail_file_name}",
        },
        'overrides': {'%bilateral_url': '{ %if( %and( enable_bilateral_scraping, '
                                        'subscription_has_download_archive, '
                                        "%is_bilateral_url( $0 ) ), $0, '' ) }",
                      '%episode_ordering_': '{ %eq( %lower( '
                                            'tv_show_by_date_episode_ordering ), $0 ) '
                                            '}',
                      '%is_bilateral_url': '{ %contains( $0, "youtube.com/playlist" ) '
                                           '}',
                      '%ordering_pair_eq': '{ %eq( [ tv_show_by_date_season_ordering, '
                                           'tv_show_by_date_episode_ordering ], [ $0, '
                                           '$1 ] ) }',
                      '%season_ordering_': '{ %eq( %lower( '
                                           'tv_show_by_date_season_ordering ), $0 ) }',
                      'assert_not_collection': True,
                      'avatar_uncropped_thumbnail_file_name': 'poster.jpg',
                      'banner_uncropped_thumbnail_file_name': 'fanart.jpg',
                      'enable_bilateral_scraping': True,
                      'enable_resolution_assert': True,
                      'enable_throttle_protection': True,
                      'episode_content_rating': 'TV-14',
                      'episode_date_standardized': '{ upload_date_standardized }',
                      'episode_file_name': 's{ upload_year }.e{ %pad_zero( %int( '
                                           '%concat( upload_month, upload_day_padded, '
                                           'upload_date_index_padded ) ), 6 ) } - { '
                                           'title_sanitized_plex }',
                      'episode_file_path': '{ %sanitize( %concat( "Season ", %string( '
                                           'upload_year ) ) ) }/{ %sanitize( %concat( '
                                           '"s", %string( upload_year ), ".e", '
                                           '%string( %pad_zero( %int( %concat( '
                                           'upload_month, upload_day_padded, '
                                           'upload_date_index_padded ) ), 6 ) ), " - '
                                           '", %string( title_sanitized_plex ) ) ) }',
                      'episode_number': '{ upload_month }{ upload_day_padded }{ '
                                        'upload_date_index_padded }',
                      'episode_number_and_padded_': '{ [ %concat( upload_month, '
                                                    'upload_day_padded, '
                                                    'upload_date_index_padded ), 6 ] '
                                                    '}',
                      'episode_number_padded': '{ %pad_zero( %int( %concat( '
                                               'upload_month, upload_day_padded, '
                                               'upload_date_index_padded ) ), 6 ) }',
                      'episode_plot': '{ webpage_url }\n\n{ description }',
                      'episode_title': '{ upload_date_standardized } - { title }',
                      'episode_year': '{ %slice( upload_date_standardized, 0, 4 ) }',
                      'file_title': '{ title_sanitized_plex }',
                      'file_uid': '{ uid_sanitized_plex }',
                      'include_sibling_metadata': False,
                      'modified_webpage_url': '{ webpage_url }',
                      'music_directory': '/music',
                      'music_video_directory': '/music_videos',
                      'resolution_assert': '{ %if( %and( enable_resolution_assert, '
                                           '%ne( height, 0 ), %not( '
                                           'resolution_assert_is_ignored ) ), '
                                           '%assert( %gte( height, '
                                           'resolution_assert_height_gte ), %concat( '
                                           '"Entry ", title, " downloaded at a low '
                                           'resolution (", resolution_readable, "), '
                                           'you\'ve probably been throttled. ", '
                                           '"Stopping further downloads, wait a few '
                                           'hours and try again. ", "Disable using '
                                           'the override variable '
                                           '`enable_resolution_assert: False`." ) ), '
                                           '"false is no-op" ) }',
                      'resolution_assert_height_gte': 361,
                      'resolution_assert_ignore_titles': '{ [  ] }',
                      'resolution_assert_is_ignored': '{ %print_if_true( %concat( '
                                                      'title, " has a match in '
                                                      'resolution_assert_ignore_titles, '
                                                      'skipping resolution assert." '
                                                      '), %contains_any( title, '
                                                      'resolution_assert_ignore_titles '
                                                      ') ) }',
                      'resolution_assert_print': True,
                      'resolution_readable': '{ width }x{ height }',
                      's01_name': '',
                      's01_url': '',
                      'season_directory_name': 'Season { upload_year }',
                      'season_number': '{ upload_year }',
                      'season_number_padded': '{ upload_year }',
                      'season_poster_file_name': '{ %sanitize( %concat( "Season ", '
                                                 '%string( upload_year ) ) ) '
                                                 '}/Season{ upload_year }.jpg',
                      'subscription_array': ['https://www.youtube.com/@novapbs'],
                      'subscription_indent_1': 'Documentaries',
                      'subscription_indent_2': 'TV-14',
                      'subscription_value': 'https://www.youtube.com/@novapbs',
                      'subscription_value_1': 'https://www.youtube.com/@novapbs',
                      'thumbnail_file_name': '{ %concat( %string( %sanitize( %concat( '
                                             '"Season ", %string( upload_year ) ) ) '
                                             '), "/", %string( %sanitize( %concat( '
                                             '"s", %string( upload_year ), ".e", '
                                             '%string( %pad_zero( %int( %concat( '
                                             'upload_month, upload_day_padded, '
                                             'upload_date_index_padded ) ), 6 ) ), " '
                                             '- ", %string( title_sanitized_plex ) ) '
                                             ') ) ) }-thumb.jpg',
                      'tv_show_by_date_episode_ordering': 'upload-month-day',
                      'tv_show_by_date_ordering_pair_validation_': '{ [ %concat( '
                                                                   'upload_month, '
                                                                   'upload_day_padded, '
                                                                   'upload_date_index_padded '
                                                                   '), 6 ] }',
                      'tv_show_by_date_season_ordering': 'upload-year',
                      'tv_show_content_rating': 'TV-14',
                      'tv_show_content_rating_default': 'TV-14',
                      'tv_show_date_range_type': 'upload_date',
                      'tv_show_directory': output_directory,
                      'tv_show_fanart_file_name': 'fanart.jpg',
                      'tv_show_genre': 'Documentaries',
                      'tv_show_genre_default': 'ytdl-sub',
                      'tv_show_name': 'NOVA PBS',
                      'tv_show_poster_file_name': 'poster.jpg',
                      'url': 'https://www.youtube.com/@novapbs',
                      'url10': '',
                      'url100': '',
                      'url11': '',
                      'url12': '',
                      'url13': '',
                      'url14': '',
                      'url15': '',
                      'url16': '',
                      'url17': '',
                      'url18': '',
                      'url19': '',
                      'url2': '',
                      'url20': '',
                      'url21': '',
                      'url22': '',
                      'url23': '',
                      'url24': '',
                      'url25': '',
                      'url26': '',
                      'url27': '',
                      'url28': '',
                      'url29': '',
                      'url3': '',
                      'url30': '',
                      'url31': '',
                      'url32': '',
                      'url33': '',
                      'url34': '',
                      'url35': '',
                      'url36': '',
                      'url37': '',
                      'url38': '',
                      'url39': '',
                      'url4': '',
                      'url40': '',
                      'url41': '',
                      'url42': '',
                      'url43': '',
                      'url44': '',
                      'url45': '',
                      'url46': '',
                      'url47': '',
                      'url48': '',
                      'url49': '',
                      'url5': '',
                      'url50': '',
                      'url51': '',
                      'url52': '',
                      'url53': '',
                      'url54': '',
                      'url55': '',
                      'url56': '',
                      'url57': '',
                      'url58': '',
                      'url59': '',
                      'url6': '',
                      'url60': '',
                      'url61': '',
                      'url62': '',
                      'url63': '',
                      'url64': '',
                      'url65': '',
                      'url66': '',
                      'url67': '',
                      'url68': '',
                      'url69': '',
                      'url7': '',
                      'url70': '',
                      'url71': '',
                      'url72': '',
                      'url73': '',
                      'url74': '',
                      'url75': '',
                      'url76': '',
                      'url77': '',
                      'url78': '',
                      'url79': '',
                      'url8': '',
                      'url80': '',
                      'url81': '',
                      'url82': '',
                      'url83': '',
                      'url84': '',
                      'url85': '',
                      'url86': '',
                      'url87': '',
                      'url88': '',
                      'url89': '',
                      'url9': '',
                      'url90': '',
                      'url91': '',
                      'url92': '',
                      'url93': '',
                      'url94': '',
                      'url95': '',
                      'url96': '',
                      'url97': '',
                      'url98': '',
                      'url99': '',
                      'urls': ['https://www.youtube.com/@novapbs']},
        "throttle_protection": {
            "enable": True,
            "sleep_per_download_s": {"max": "28.4", "min": "13.8"},
            "sleep_per_request_s": {"max": "0.75", "min": "0.0"},
            "sleep_per_subscription_s": {"max": "26.1", "min": "16.3"},
        },
        "video_tags": {
            "contentRating": "{episode_content_rating}",
            "date": "{episode_date_standardized}",
            "episode_id": "{episode_number}",
            "genre": "{tv_show_genre}",
            "show": "{tv_show_name}",
            "synopsis": "{episode_plot}",
            "title": "{episode_title}",
            "year": "{episode_year}",
        },
    }