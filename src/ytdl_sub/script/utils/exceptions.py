from abc import ABC

from ytdl_sub.utils.exceptions import ValidationException


class UserException(ValidationException, ABC):
    """It's the user's fault!"""


class InvalidSyntaxException(UserException):
    """Syntax is incorrect"""


class IncompatibleFunctionArguments(UserException):
    """Function has invalid arguments"""


class FunctionDoesNotExist(UserException):
    """Tried to use a function that does not exist"""


class CycleDetected(UserException):
    """A cycle exists within a user's script"""


class FunctionRuntimeException(ValueError):
    """Exception thrown when a ytdl-sub function has an error occur at runtime"""


class UserThrownRuntimeError(ValidationException):
    """An error explicitly thrown by the user via a function"""


class _UnreachableSyntaxException(InvalidSyntaxException):
    """For use in places where code _should_ never reach, but might from bugs"""


UNREACHABLE = _UnreachableSyntaxException(
    "If you see this error, you have discovered a bug in the script parser!\n"
    "Please upload your config/subscription file(s) to and make a GitHub issue at "
    "https://github.com/jmbannon/ytdl-sub/issues"
)
