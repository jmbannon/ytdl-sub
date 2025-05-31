from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import ReturnableArgument
from ytdl_sub.utils.logger import Logger

logger = Logger.get(name="preset")


class PrintFunctions:
    @staticmethod
    def print(
        message: AnyArgument, passthrough: ReturnableArgument
    ) -> ReturnableArgument:
        """
        :description:
          Print the ``message`` and return ``passthrough``.
        """
        logger.info(str(message))
        return passthrough

    @staticmethod
    def print_if_true(
        message: AnyArgument, passthrough: ReturnableArgument
    ) -> ReturnableArgument:
        """
        :description:
          Print the ``message`` if ``passthrough`` evaluates to ``true``. Return ``passthrough``.
        """
        if passthrough.value:
            logger.info(str(message))
        return passthrough

    @staticmethod
    def print_if_false(
        message: AnyArgument, passthrough: ReturnableArgument
    ) -> ReturnableArgument:
        """
        :description:
          Print the ``message`` if ``passthrough`` evaluates to ``false``. Return ``passthrough``.
        """
        if not passthrough.value:
            logger.info(str(message))
        return passthrough
