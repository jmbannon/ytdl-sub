from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import ReturnableArgument
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError


class ErrorFunctions:
    @staticmethod
    def throw(error_message: String) -> AnyArgument:
        """
        Explicitly throw an error with the provided error message.
        """
        raise UserThrownRuntimeError(error_message)

    @staticmethod
    def assert_(value: ReturnableArgument, assert_message: String) -> ReturnableArgument:
        """
        Explicitly throw an error with the provided assert message if ``value`` evaluates to False.
        If it evaluates to True, it will return ``value``.
        """
        if not bool(value.value):
            raise UserThrownRuntimeError(assert_message)
        return value
