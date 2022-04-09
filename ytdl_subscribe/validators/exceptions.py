class ValidationException(ValueError):
    """Any user-caused configuration error should result in this error"""


class StringFormattingException(ValidationException):
    """Tried to format a string but failed due to user misconfigured variables"""


class StringFormattingVariableNotFoundException(StringFormattingException):
    """Tried to format a string but the variable was not found"""
