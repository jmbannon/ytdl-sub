from abc import ABC

from ytdl_sub.utils.exceptions import ValidationException

###################################################################################################
# USER EXCEPTIONS


class UserException(ValidationException, ABC):
    """It's the user's fault!"""


class InvalidSyntaxException(UserException):
    """Syntax is incorrect"""


class InvalidVariableName(UserException):
    """Variable name is invalid"""


class InvalidFunctionName(UserException):
    """Custom function name is invalid"""


class InvalidCustomFunctionArguments(UserException):
    """Custom function arguments are invalid (i.e. they do not increment)"""


class InvalidCustomFunctionArgumentName(UserException):
    """Custom function argument name (i.e. $0) is invalid"""


class IncompatibleFunctionArguments(UserException):
    """Function has invalid arguments"""


class FunctionDoesNotExist(UserException):
    """Tried to use a function that does not exist"""


class VariableDoesNotExist(UserException):
    """Tried to use a variable that does not exist"""


class ScriptBuilderMissingDefinitions(UserException):
    """Tried to build an incomplete ScriptBuilder"""


class CycleDetected(UserException):
    """A cycle exists within a user's script"""


class UserThrownRuntimeError(ValidationException):
    """An error explicitly thrown by the user via a function"""


class _UnreachableSyntaxException(InvalidSyntaxException):
    """For use in places where code _should_ never reach, but might from bugs"""


UNREACHABLE = _UnreachableSyntaxException(
    "If you see this error, you have discovered a bug in the script parser!\n"
    "Please upload your config/subscription file(s) to and make a GitHub issue at "
    "https://github.com/jmbannon/ytdl-sub/issues"
)

###################################################################################################
# RUNTIME EXCEPTIONS


class RuntimeException(ValueError, ABC):
    """Exception thrown at runtime during resolution"""


class ScriptVariableNotResolved(RuntimeException):
    """Tried to get a variable's resolved value from a script, but has not resolved yet"""


class FunctionRuntimeException(RuntimeException):
    """Exception thrown when a ytdl-sub function has an error occur at runtime"""


class KeyNotHashableRuntimeException(RuntimeException):
    """Map tried to use a non-hashable key at runtime"""


class ArrayValueDoesNotExist(RuntimeException):
    """Tried to get an index of a value in an Array that does not exist"""


class FunctionDoesNotExistRuntimeException(RuntimeException):
    """Tried to get a function that does not exist"""


class KeyDoesNotExistRuntimeException(RuntimeException):
    """Tried to access a key on a map that does not exist, with no default"""
