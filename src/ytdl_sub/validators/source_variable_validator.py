from ytdl_sub.utils.exceptions import InvalidVariableNameException
from ytdl_sub.validators.string_formatter_validators import is_valid_source_variable_name
from ytdl_sub.validators.validators import ListValidator
from ytdl_sub.validators.validators import StringValidator


class SourceVariableNameValidator(StringValidator):
    _expected_value_type_name = "source variable name"

    def __init__(self, name, value):
        super().__init__(name, value)
        try:
            _ = is_valid_source_variable_name(self.value, raise_exception=True)
        except InvalidVariableNameException as exc:
            raise self._validation_exception(exc) from exc


class SourceVariableNameListValidator(ListValidator[SourceVariableNameValidator]):
    _inner_list_type = SourceVariableNameValidator
    _expected_value_type_name = "source variable name list"
