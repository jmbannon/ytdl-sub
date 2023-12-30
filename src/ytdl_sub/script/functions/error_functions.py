from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import ReturnableArgument
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError


class ErrorFunctions:
    @staticmethod
    def throw(error_message: String) -> AnyArgument:
        """
        :description:
          Explicitly throw an error with the provided error message.
        """
        raise UserThrownRuntimeError(error_message)

    @staticmethod
    def assert_(value: ReturnableArgument, assert_message: String) -> ReturnableArgument:
        """
        :description:
          Explicitly throw an error with the provided assert message if ``value`` evaluates to
          False. If it evaluates to True, it will return ``value``.
        """
        if not bool(value.value):
            raise UserThrownRuntimeError(assert_message)
        return value

    @staticmethod
    def assert_then(
        value: AnyArgument, ret: ReturnableArgument, assert_message: String
    ) -> ReturnableArgument:
        """
        :description:
          Explicitly throw an error with the provided assert message if ``value`` evaluates to
          False. If it evaluates to True, it will return ``ret``.
        """
        if not bool(value.value):
            raise UserThrownRuntimeError(assert_message)
        return ret

    @staticmethod
    def assert_eq(
        value: ReturnableArgument, equals: AnyArgument, assert_message: String
    ) -> ReturnableArgument:
        """
        :description:
          Explicitly throw an error with the provided assert message if ``value`` does not equal
          ``equals``. If they do equal, then return ``value``.
        """
        if not value.value == equals.value:
            raise UserThrownRuntimeError(assert_message)
        return value

    @staticmethod
    def assert_ne(
        value: ReturnableArgument, equals: AnyArgument, assert_message: String
    ) -> ReturnableArgument:
        """
        :description:
          Explicitly throw an error with the provided assert message if ``value`` equals
          ``equals``. If they do equal, then return ``value``.
        """
        if value.value == equals.value:
            raise UserThrownRuntimeError(assert_message)
        return value
