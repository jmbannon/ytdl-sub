from abc import ABC

from ytdl_sub.utils.exceptions import ValidationException


class UserException(ValidationException, ABC):
    """It's the user's fault!"""


class InvalidSyntaxException(UserException):
    """Syntax is incorrect"""


class IncompatibleFunctionArguments(UserException):
    """Function has invalid arguments"""


class UnreachableSyntaxException(InvalidSyntaxException):
    """For use in places where code _should_ never reach, but might from bugs"""


UNREACHABLE = UnreachableSyntaxException(
    "If you see this error, you have discovered a bug in the script parser!\n"
    "Please upload your config/subscription file(s) to and make a GitHub issue at "
    "https://github.com/jmbannon/ytdl-sub/issues"
)
