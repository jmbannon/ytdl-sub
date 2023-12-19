from ytdl_sub.script.utils.name_validation import is_valid_name
from ytdl_sub.utils.exceptions import InvalidVariableNameException
from ytdl_sub.validators.validators import ListValidator
from ytdl_sub.validators.validators import StringValidator


class SourceVariableNameValidator(StringValidator):
    _expected_value_type_name = "source variable name"

    def __init__(self, name, value):
        super().__init__(name, value)

        if not is_valid_name(value):
            raise self._validation_exception(
                f"Variable with name {name} is invalid. Names must be"
                " lower_snake_cased and begin with a letter.",
                exception_class=InvalidVariableNameException,
            )


class SourceVariableNameListValidator(ListValidator[SourceVariableNameValidator]):
    _inner_list_type = SourceVariableNameValidator
    _expected_value_type_name = "source variable name list"
