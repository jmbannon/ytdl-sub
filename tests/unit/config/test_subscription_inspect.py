from pathlib import Path

from resources import expected_json

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.script.script import Script
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.script import ScriptUtils


def _ensure_partial_resolve(
    sub: Subscription, preset_type: str, built_in_unresolvable: bool
) -> Script:
    unresolvable = sub.plugins.get_all_variables(
        additional_options=[sub.downloader_options, sub.output_options]
    )
    unresolvable.add("entry_metadata")
    unresolvable.add("sibling_metadata")

    if built_in_unresolvable:
        unresolvable.update(VARIABLES.scripts().keys())

    script = sub.overrides.script.add(
        {
            f"{preset_type}_directory": "tv_show_directory_path",
            f"{preset_type}_directory_sanitized": "tv_show_directory_path",
        }
    )
    partial_script = script.resolve_partial(unresolvable=unresolvable)

    out = {
        name: ScriptUtils.to_native_script(partial_script._variables[name])
        for name in sub.overrides.keys
        if not name.startswith("%")
    }

    assert out == expected_json(out, f"{preset_type}/inspect_built_in_unresolvable_overrides.json")

    out = {
        name: ScriptUtils.to_native_script(partial_script._variables[name])
        for name in partial_script.variable_names
    }

    assert out == expected_json(out, f"{preset_type}/inspect_built_in_unresolvable_all.json")


def test_partial_resolve_tv_show(config_file: ConfigFile, tv_show_subscriptions_path: Path):
    _ensure_partial_resolve(
        sub=Subscription.from_file_path(
            config=config_file, subscription_path=tv_show_subscriptions_path
        )[0],
        preset_type="tv_show",
        built_in_unresolvable=True,
    )


def test_partial_resolve_tv_show_full(config_file: ConfigFile, tv_show_subscriptions_path: Path):
    _ensure_partial_resolve(
        sub=Subscription.from_file_path(
            config=config_file, subscription_path=tv_show_subscriptions_path
        )[0],
        preset_type="tv_show",
        built_in_unresolvable=False,
    )


def test_partial_resolve_music(default_config: ConfigFile, music_subscriptions_path: Path):
    _ensure_partial_resolve(
        sub=Subscription.from_file_path(
            config=default_config, subscription_path=music_subscriptions_path
        )[0],
        preset_type="music",
        built_in_unresolvable=True,
    )


def test_partial_resolve_music_full(default_config: ConfigFile, music_subscriptions_path: Path):
    _ensure_partial_resolve(
        sub=Subscription.from_file_path(
            config=default_config, subscription_path=music_subscriptions_path
        )[0],
        preset_type="music",
        built_in_unresolvable=False,
    )


def test_partial_resolve_music_video(
    default_config: ConfigFile, music_video_subscription_path: Path
):
    _ensure_partial_resolve(
        sub=Subscription.from_file_path(
            config=default_config, subscription_path=music_video_subscription_path
        )[0],
        preset_type="music_video",
        built_in_unresolvable=False,
    )


def test_partial_resolve_music_video_full(
    default_config: ConfigFile, music_video_subscription_path: Path
):
    _ensure_partial_resolve(
        sub=Subscription.from_file_path(
            config=default_config, subscription_path=music_video_subscription_path
        )[0],
        preset_type="music_video",
        built_in_unresolvable=True,
    )
