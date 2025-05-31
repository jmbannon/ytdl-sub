from typing import Optional

from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import ReturnableArgument
from ytdl_sub.utils.logger import Logger

logger = Logger.get(name="preset")


def _log(message: AnyArgument, level: Optional[Integer]) -> None:
    if level is None:
        logger.info(str(message))
        return

    level_value: int = level.native
    if level_value < 0:
        logger.debug(str(message))
    elif level_value == 0:
        logger.info(str(message))
    elif level_value == 1:
        logger.warning(str(message))
    else:  # > 1
        logger.error(str(message))


class PrintFunctions:
    @staticmethod
    def print(
        message: AnyArgument, passthrough: ReturnableArgument, level: Optional[Integer] = None
    ) -> ReturnableArgument:
        """
        :description:
          Print the ``message`` and return ``passthrough``.
          Optionally can pass level, where < 0 is debug, 0 is info, 1 is warning, > 1 is error.
          Defaults to info.
        """
        _log(message=message, level=level)
        return passthrough

    @staticmethod
    def print_if_true(
        message: AnyArgument, passthrough: ReturnableArgument, level: Optional[Integer] = None
    ) -> ReturnableArgument:
        """
        :description:
          Print the ``message`` if ``passthrough`` evaluates to ``true``. Return ``passthrough``.
          Optionally can pass level, where < 0 is debug, 0 is info, 1 is warning, > 1 is error.
          Defaults to info.
        """
        if passthrough.value:
            _log(message=message, level=level)
        return passthrough

    @staticmethod
    def print_if_false(
        message: AnyArgument, passthrough: ReturnableArgument, level: Optional[Integer] = None
    ) -> ReturnableArgument:
        """
        :description:
          Print the ``message`` if ``passthrough`` evaluates to ``false``. Return ``passthrough``.
          Optionally can pass level, where < 0 is debug, 0 is info, 1 is warning, > 1 is error.
          Defaults to info.
        """
        if not passthrough.value:
            _log(message=message, level=level)
        return passthrough
