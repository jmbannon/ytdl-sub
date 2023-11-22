from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import Boolean
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
    def assert_(condition: Boolean, assert_message: String) -> Boolean:
        """
        Explicitly throw an error with the provided assert message if ``condition`` is False.
        """
        if not condition.value:
            raise UserThrownRuntimeError(assert_message)
        return condition
