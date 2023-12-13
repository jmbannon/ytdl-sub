import re

from ytdl_sub.script.functions import Functions
from ytdl_sub.script.utils.exceptions import InvalidFunctionName
from ytdl_sub.script.utils.exceptions import InvalidVariableName

_NAME_REGEX_VALIDATOR = re.compile(r"^[a-z][a-z0-9_]*$")


def is_valid_name(name: str) -> bool:
    """
    Returns
    -------
    True if the name adheres to the ``snake_case`` format. False otherwise.
    """
    return re.match(_NAME_REGEX_VALIDATOR, name) is not None


def validate_variable_name(variable_name: str) -> str:
    """
    Raises
    ------
    InvalidVariableName
        if the variable name is invalid
    """
    if not is_valid_name(variable_name):
        raise InvalidVariableName(
            f"Variable name '{variable_name}' is invalid:"
            " Names must be lower_snake_cased and begin with a letter."
        )

    if Functions.is_built_in(variable_name):
        raise InvalidVariableName(
            f"Variable name '{variable_name}' is invalid:"
            " The name is used by a built-in function and cannot be overwritten."
        )

    return variable_name


def validate_custom_function_name(custom_function_name: str) -> None:
    """
    Raises
    ------
    InvalidFunctionName
        If the function name is invalid
    InvalidVariableName
        if the variable name is invalid
    """
    if not is_valid_name(custom_function_name):
        raise InvalidFunctionName(
            f"Custom function name '%{custom_function_name}' is invalid:"
            " Names must be %lower_snake_cased and begin with a letter."
        )

    if Functions.is_built_in(custom_function_name):
        raise InvalidFunctionName(
            f"Custom function name '%{custom_function_name}' is invalid:"
            " The name is used by a built-in function and cannot be overwritten."
        )
