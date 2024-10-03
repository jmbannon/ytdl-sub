import contextlib
import json
import logging
import os
import shlex
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from unittest.mock import patch

import pytest
from expected_download import _get_files_in_directory
from resources import copy_file_fixture
from resources import file_fixture_path
from yt_dlp.utils import sanitize_filename

from ytdl_sub.cli.entrypoint import main
from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.entries.script.custom_functions import CustomFunctions
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.subscriptions.subscription_download import SubscriptionDownload
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.logger import LoggerLevels
from ytdl_sub.utils.yaml import load_yaml


@pytest.fixture(autouse=True)
def register_custom_functions():
    """
    Clean logs after every test
    """
    CustomFunctions.register()


@pytest.fixture(autouse=True)
def cleanup_debug_file():
    """
    Clean logs after every test
    """
    with tempfile.NamedTemporaryFile(prefix="ytdl-sub.", delete=False) as debug_log_file:
        Logger._DEBUG_LOGGER_FILE = debug_log_file

    Logger.set_log_level(log_level_name=LoggerLevels.DEBUG.name)
    try:
        yield
    finally:
        Logger.cleanup()


@pytest.fixture
def working_directory() -> str:
    """
    Any time the working directory is used, ensure no files remain on cleaning it up
    """
    logger = Logger.get("test")

    with tempfile.TemporaryDirectory() as temp_dir:

        def _assert_working_directory_empty(self, is_error: bool = False):
            files = [str(file_path) for file_path in _get_files_in_directory(temp_dir)]
            num_files = len(files)
            if os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir)

            if not is_error:
                if num_files > 0:
                    logger.error("left-over files in working dir:\n%s", "\n".join(files))
                assert num_files == 0

        with patch.object(
            SubscriptionDownload,
            "_delete_working_directory",
            new=_assert_working_directory_empty,
        ):
            yield temp_dir


@pytest.fixture()
def output_directory() -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture()
def reformat_directory() -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@contextlib.contextmanager
def assert_logs(
    logger: logging.Logger,
    expected_message: str,
    log_level: str = "debug",
    expected_occurrences: Optional[int] = None,
):
    """
    Patches any function, but calls the original function.
    Intended to see if the particular function is called.
    """
    occurrences = 0
    debug_logger = Logger.get()

    def _wrapped_debug(*args, **kwargs):
        debug_logger.info(*args, **kwargs)

    with patch.object(logger, log_level, wraps=_wrapped_debug) as patched_debug:
        yield

    for call_args in patched_debug.call_args_list:
        occurrences += int(expected_message in call_args.args[0])

    if expected_occurrences is not None:
        assert (
            occurrences == expected_occurrences
        ), f"{expected_message} was expected {expected_occurrences} times, got {occurrences}"
    else:
        assert occurrences > 0, f"{expected_message} was not found in a logger.debug call"


def preset_dict_to_dl_args(preset_dict: Dict) -> str:
    """
    Parameters
    ----------
    preset_dict
        Preset dict to convert

    Returns
    -------
    Preset dict converted to CLI parameters
    """

    def _maybe_quote_value(value: Any):
        if isinstance(value, str) and " " in value:
            return f'"{value}"'
        return value

    def _recursive_preset_args(cli_key: str, current_value: Dict | Any) -> List[str]:
        if isinstance(current_value, dict):
            preset_args: List[str] = []
            for v_key, v_value in sorted(current_value.items()):
                preset_args.extend(
                    _recursive_preset_args(
                        cli_key=f"{cli_key}.{v_key}" if cli_key else v_key, current_value=v_value
                    )
                )
            return preset_args
        elif isinstance(current_value, list):
            return [
                f"--{cli_key}[{idx + 1}] {_maybe_quote_value(current_value[idx])}"
                for idx in range(len(current_value))
            ]
        else:
            return [f"--{cli_key} {_maybe_quote_value(current_value)}"]

    return " ".join(_recursive_preset_args(cli_key="", current_value=preset_dict))


@pytest.fixture
def preset_dict_to_subscription_yaml_generator() -> Callable:
    @contextlib.contextmanager
    def _preset_dict_to_subscription_yaml_generator(subscription_name: str, preset_dict: Dict):
        subscription_dict = {subscription_name: preset_dict}
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp_file:
            tmp_file.write(json.dumps(subscription_dict).encode("utf-8"))

        try:
            yield tmp_file.name
        finally:
            FileHandler.delete(tmp_file.name)

    return _preset_dict_to_subscription_yaml_generator


###################################################################################################
# Staging a mock already-existing download


@pytest.fixture
def pz_channel_mock_downloaded_with_archive_factory(output_directory: Path) -> Callable:
    def _pz_channel_mock_downloaded_with_archive_factory(tv_show_name: str, archive_file_name: str):
        subscription_path = Path(output_directory) / sanitize_filename(tv_show_name)
        copy_file_fixture(
            fixture_name="pz_download_archive.json",
            output_file_path=subscription_path / archive_file_name,
        )

        with open(
            file_fixture_path("pz_download_archive.json"), "r", encoding="utf-8"
        ) as archive_file:
            archive_dict = json.load(archive_file)

        assert isinstance(archive_dict, dict)
        for uid, metadata in archive_dict.items():
            assert isinstance(metadata, dict)
            for filename in metadata["file_names"]:
                assert isinstance(filename, str)
                output_file_path = subscription_path / filename
                if filename.endswith(".mp4"):
                    copy_file_fixture("sample_vid.mp4", output_file_path)
                else:
                    copy_file_fixture("empty.txt", output_file_path)

    return _pz_channel_mock_downloaded_with_archive_factory


###################################################################################################
# Example config fixtures


def _load_config(config_path: Path, working_directory: str) -> ConfigFile:
    config_dict = load_yaml(file_path=config_path)
    config_dict["configuration"]["working_directory"] = working_directory

    return ConfigFile.from_dict(config_dict)


@pytest.fixture()
def music_video_subscription_path() -> Path:
    return Path("examples/music_video_subscriptions.yaml")


@pytest.fixture()
def tv_show_config_path() -> str:
    return "examples/advanced/tv_show_config.yaml"


@pytest.fixture()
def tv_show_config(working_directory, tv_show_config_path) -> ConfigFile:
    return _load_config(config_path=Path(tv_show_config_path), working_directory=working_directory)


@pytest.fixture()
def tv_show_subscriptions_path() -> Path:
    return Path("examples/tv_show_subscriptions.yaml")


@pytest.fixture()
def advanced_tv_show_subscriptions_path() -> Path:
    return Path("examples/advanced/tv_show_subscriptions.yaml")


@pytest.fixture()
def default_config(working_directory) -> ConfigFile:
    return ConfigFile.from_dict({"configuration": {"working_directory": working_directory}})


@pytest.fixture()
def default_config_path(default_config) -> str:
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp_file:
        tmp_file.write(json.dumps(default_config._value).encode("utf-8"))

    try:
        yield tmp_file.name
    finally:
        FileHandler.delete(tmp_file.name)


@pytest.fixture()
def music_subscriptions_path() -> Path:
    return Path("examples/music_subscriptions.yaml")


def mock_run_from_cli(args: str) -> List[Subscription]:
    args_list = ["ytdl-sub"] + shlex.split(args)
    with patch.object(sys, "argv", args_list):
        return main()
