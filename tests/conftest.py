import contextlib
import logging
from typing import Callable
from unittest.mock import MagicMock
from unittest.mock import patch

from ytdl_sub.utils.logger import Logger


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
