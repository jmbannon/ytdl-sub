import contextlib
import json
import logging
import tempfile
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from unittest.mock import patch

import pytest

from ytdl_sub.utils.logger import Logger


@pytest.fixture
def working_directory() -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture()
def output_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@contextlib.contextmanager
def assert_debug_log(logger: logging.Logger, expected_message: str):
    """
    Patches any function, but calls the original function.
    Intended to see if the particular function is called.
    """
    debug_logger = Logger.get()

    def _wrapped_debug(*args, **kwargs):
        debug_logger.info(*args, **kwargs)

    with patch.object(logger, "debug", wraps=_wrapped_debug) as patched_debug:
        yield

    for call_args in patched_debug.call_args_list:
        if expected_message in call_args.args[0]:
            return

    assert False, f"{expected_message} was not found in a logger.debug call"


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
                f"--{cli_key}[{idx + 1}] {current_value[idx]}" for idx in range(len(current_value))
            ]
        else:
            return [f"--{cli_key} {current_value}"]

    return " ".join(_recursive_preset_args(cli_key="", current_value=preset_dict))


@pytest.fixture
def preset_dict_to_subscription_yaml_generator() -> Callable:
    @contextlib.contextmanager
    def _preset_dict_to_subscription_yaml_generator(subscription_name: str, preset_dict: Dict):
        subscription_dict = {subscription_name: preset_dict}
        with tempfile.NamedTemporaryFile(suffix=".yaml") as tmp_file:
            tmp_file.write(json.dumps(subscription_dict).encode("utf-8"))
            tmp_file.flush()
            yield tmp_file.name

    return _preset_dict_to_subscription_yaml_generator
