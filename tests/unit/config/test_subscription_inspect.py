from pathlib import Path

from resources import expected_json

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.script import ScriptUtils


def test_built_in_unresolvable(docker_default_subscription_path: Path):
    sub = Subscription.from_file_path(
        config=ConfigFile.from_file_path("docker/root/defaults/config.yaml"),
        subscription_path=docker_default_subscription_path,
    )[0]

    unresolvable = sub.plugins.get_all_variables(
        additional_options=[sub.downloader_options, sub.output_options]
    )
    unresolvable.add("entry_metadata")
    unresolvable.add("sibling_metadata")
    unresolvable.update(VARIABLES.scripts().keys())

    script = sub.overrides.script.add(
        {
            "tv_show_directory": "tv_show_directory_path",
            "tv_show_directory_sanitized": "tv_show_directory_path",
        }
    )
    partial_script = script.resolve_partial(unresolvable=unresolvable)

    out = {
        name: ScriptUtils.to_native_script(partial_script._variables[name])
        for name in sub.overrides.keys
        if not name.startswith("%")
    }

    assert out == expected_json(out, "inspect_built_in_unresolvable_overrides.json")

    out = {
        name: ScriptUtils.to_native_script(partial_script._variables[name])
        for name in script.variable_names
    }

    assert out == expected_json(out, "inspect_built_in_unresolvable_all.json")


def test_bare_minimum_unresolvable(docker_default_subscription_path: Path, output_directory: str):
    sub = Subscription.from_file_path(
        config=ConfigFile.from_file_path("docker/root/defaults/config.yaml"),
        subscription_path=docker_default_subscription_path,
    )[0]

    unresolvable = sub.plugins.get_all_variables(
        additional_options=[sub.downloader_options, sub.output_options]
    )
    unresolvable.add("entry_metadata")
    unresolvable.add("sibling_metadata")

    script = sub.overrides.script.add(
        {
            "tv_show_directory": "tv_show_directory_path",
            "tv_show_directory_sanitized": "tv_show_directory_path",
        }
    )
    partial_script = script.resolve_partial(unresolvable=unresolvable)

    out = {
        name: ScriptUtils.to_native_script(partial_script._variables[name])
        for name in sub.overrides.keys
        if not name.startswith("%")
    }

    assert out == expected_json(out, "inspect_unresolvable_all.json")

    out = {
        name: ScriptUtils.to_native_script(partial_script._variables[name])
        for name in script.variable_names
    }

    assert out == expected_json(out, "inspect_unresolvable_overrides.json")
