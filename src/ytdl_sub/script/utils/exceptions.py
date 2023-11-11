from ytdl_sub.utils.exceptions import ValidationException


class InvalidSyntaxException(ValidationException):
    """Syntax is incorrect"""


class UnreachableSyntaxException(InvalidSyntaxException):
    """For use in places where code _should_ never reach, but might from bugs"""