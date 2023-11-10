from ytdl_sub.utils.exceptions import ValidationException


class InvalidSyntaxException(ValidationException):
    """Syntax is incorrect"""


class NonFormattedInvalidSyntaxException(InvalidSyntaxException):
    """
    Syntax is incorrect, and the exception itself has not been formatted yet to be user-facing
    """
