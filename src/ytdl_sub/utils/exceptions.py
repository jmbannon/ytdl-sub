class ValidationException(ValueError):
    """Any user-caused configuration error should result in this error"""


class StringFormattingException(ValidationException):
    """Tried to format a string but failed due to user misconfigured variables"""


class StringFormattingVariableNotFoundException(StringFormattingException):
    """Tried to format a string but the variable was not found"""


class InvalidVariableNameException(ValidationException):
    """A user defined variable name is invalid"""


class DownloadArchiveException(ValueError):
    """Any user or file errors caused by download archive or mapping files"""


class FileNotFoundException(ValidationException):
    """Any user file that's expected to exist, but is not found"""


class InvalidYamlException(ValidationException):
    """User yaml that is invalid"""


class RegexNoMatchException(ValidationException):
    """Regex failed to match during download"""


class InvalidDlArguments(ValidationException):
    """dl arguments that are invalid"""


class FileNotDownloadedException(ValueError):
    """ytdlp failed to download something"""


class ExperimentalFeatureNotEnabled(ValidationException):
    """Feature is not enabled for usage"""
