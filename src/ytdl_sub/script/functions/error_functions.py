from ytdl_sub.script.types.resolvable import AnyType
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError


class ErrorFunctions:
    @staticmethod
    def throw(error_message: String) -> AnyType:
        raise UserThrownRuntimeError(error_message)

    @staticmethod
    def assert_(condition: Boolean, assert_message: String) -> Boolean:
        if not condition.value:
            raise UserThrownRuntimeError(assert_message)
        return condition
