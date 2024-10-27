import json
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.script.functions import Functions
from ytdl_sub.script.types.array import UnresolvedArray
from ytdl_sub.script.types.function import Argument
from ytdl_sub.script.types.function import BuiltInFunction
from ytdl_sub.script.types.function import CustomFunction
from ytdl_sub.script.types.function import Function
from ytdl_sub.script.types.map import UnresolvedMap
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import Lambda
from ytdl_sub.script.types.resolvable import NonHashable
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.types.variable import FunctionArgument
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exception_formatters import ParserExceptionFormatter
from ytdl_sub.script.utils.exceptions import UNREACHABLE
from ytdl_sub.script.utils.exceptions import CycleDetected
from ytdl_sub.script.utils.exceptions import FunctionDoesNotExist
from ytdl_sub.script.utils.exceptions import IncompatibleFunctionArguments
from ytdl_sub.script.utils.exceptions import InvalidCustomFunctionArgumentName
from ytdl_sub.script.utils.exceptions import InvalidSyntaxException
from ytdl_sub.script.utils.exceptions import InvalidVariableName
from ytdl_sub.script.utils.exceptions import UserException
from ytdl_sub.script.utils.exceptions import VariableDoesNotExist
from ytdl_sub.script.utils.name_validation import validate_variable_name

# pylint: disable=invalid-name
# pylint: disable=too-many-branches
# pylint: disable=too-many-return-statements
# pylint: disable=consider-using-ternary


class ParsedArgType(Enum):
    SCRIPT = "script"
    FUNCTION = "function"
    ARRAY = "array"
    MAP_KEY = "map key"
    MAP_VALUE = "map value"


BRACKET_NOT_CLOSED = InvalidSyntaxException("Bracket not properly closed")

NUMERICS_ONLY_ARGS = InvalidSyntaxException(
    "Numerics can only be used as arguments to functions, maps, or arrays"
)
NUMERICS_INVALID_CHAR = InvalidSyntaxException("Invalid value when parsing a numeric")


STRINGS_ONLY_ARGS = InvalidSyntaxException(
    "Strings can only be used as arguments to functions, maps, or arrays"
)
STRINGS_NOT_CLOSED = InvalidSyntaxException(
    "String was not closed properly. "
    "Must open and close with the same type of quote (single/double)"
)

BOOLEAN_ONLY_ARGS = InvalidSyntaxException(
    "Booleans can only be used as arguments to functions, maps, or arrays"
)

CUSTOM_FUNCTION_ARGUMENTS_ONLY_ARGS = InvalidSyntaxException(
    "Custom function arguments can only be used as arguments to functions, maps, or arrays"
)

FUNCTION_INVALID_CHAR = InvalidSyntaxException("Invalid value when parsing a function")

BRACKET_INVALID_CHAR = InvalidSyntaxException("Invalid value within brackets")


def _UNEXPECTED_CHAR_ARGUMENT(arg_type: ParsedArgType):
    return InvalidSyntaxException(f"Unexpected character when parsing {arg_type.value} arguments")


def _UNEXPECTED_COMMA_ARGUMENT(arg_type: ParsedArgType):
    return InvalidSyntaxException(f"Unexpected comma when parsing {arg_type.value} arguments")


MAP_KEY_WITH_NO_VALUE = InvalidSyntaxException("Map has a key with no value")
MAP_KEY_MULTIPLE_VALUES = InvalidSyntaxException(
    "Map key has multiple values when there should only be one"
)
MAP_MISSING_KEY = InvalidSyntaxException("Map has a missing key")
MAP_KEY_NOT_HASHABLE = InvalidSyntaxException(
    "Map key must be a hashable type (Integer, Float, Boolean, String)"
)


def _is_variable_start(char: str) -> bool:
    return char.isalpha() and char.islower()


def _is_function_name_char(char: str) -> bool:
    return (char.isalpha() and char.islower()) or char.isnumeric() or char == "_"


def _is_numeric_start(char: str) -> bool:
    return char.isnumeric() or char in (".", "-")


def _is_string_start_single_char(char: Optional[str]) -> bool:
    return char in ["'", '"']


def _is_string_start_multi_char(string: Optional[str]) -> bool:
    return string in ["'''", '"""']


def _is_null(string: Optional[str]) -> bool:
    return string and string.lower() == "null"


def _is_breakable(char: str) -> bool:
    return char in ["}", ",", ")", "]", ":"] or char.isspace()


def _is_boolean_true(string: Optional[str]) -> bool:
    return string and string.lower() == "true"


def _is_boolean_false(string: Optional[str]) -> bool:
    return string and string.lower() == "false"


def _is_custom_function_argument_start(char: str) -> bool:
    return char == "$"


class _Parser:
    def __init__(
        self,
        text: str,
        name: Optional[str],
        custom_function_names: Optional[Set[str]],
        variable_names: Optional[Set[str]],
    ):
        self._text = text
        self._name = name
        self._custom_function_names = custom_function_names
        self._variable_names = variable_names
        self._pos = 0
        self._error_highlight_pos = 0
        self._ast: List[Argument] = []

        self._bracket_counter_pos_stack: List[int] = []
        self._bracket_counter = 0
        self._literal_str = ""

        try:
            self._syntax_tree = self._parse()
        except UserException as exc:
            raise ParserExceptionFormatter(
                self._text, self._error_highlight_pos, self._pos, exc
            ).highlight() from exc

    @property
    def ast(self) -> SyntaxTree:
        """
        Returns
        -------
        Abstract syntax tree of the parsed text
        """
        return self._syntax_tree

    def _set_highlight_position(self, pos: Optional[int] = None) -> None:
        self._error_highlight_pos = pos if pos is not None else self._pos

    def _read(self, increment_pos: bool = True, length: int = 1) -> Optional[str]:
        if isinstance(self._text, int):
            pass
        if self._pos >= len(self._text):
            return None

        try:
            ch = self._text[self._pos : (self._pos + length)]
        except IndexError:
            return None

        if increment_pos:
            self._pos += length
        return ch

    def _parse_variable(self) -> Variable:
        var_name = ""
        variable_start_pos = self._pos
        while ch := self._read(increment_pos=False):
            if ch.isspace() and not var_name:
                self._pos += 1
                continue
            if _is_breakable(ch):
                break

            if not var_name:
                variable_start_pos = self._pos

            var_name += ch
            self._pos += 1

        try:
            validate_variable_name(var_name)
        except InvalidVariableName:
            self._set_highlight_position(variable_start_pos)
            raise

        if self._variable_names is not None and var_name not in self._variable_names:
            self._set_highlight_position(variable_start_pos)
            raise VariableDoesNotExist(f"Variable {var_name} does not exist.")

        return Variable(var_name)

    def _parse_custom_function_argument(self) -> FunctionArgument:
        """
        Begin parsing function args after the first ``$``, i.e. ``$0``
        """
        var_name = ""
        variable_start_pos = self._pos
        while ch := self._read(increment_pos=False):
            if ch.isspace() and not var_name:
                raise InvalidCustomFunctionArgumentName(
                    "Custom function arguments, denoted by $, cannot have a space proceeding it."
                )
            if _is_breakable(ch):
                break

            var_name += ch
            self._pos += 1

        if not var_name.isnumeric():
            self._set_highlight_position(variable_start_pos)
            raise InvalidCustomFunctionArgumentName(
                "Custom function arguments must be numeric and increment starting from zero."
            )

        return FunctionArgument.from_idx(idx=int(var_name), custom_function_name=self._name)

    def _parse_numeric(self) -> Integer | Float:
        numeric_string = ""

        if self._read(increment_pos=False) == "-":
            numeric_string += "-"
            self._pos += 1
        if has_decimal := self._read(increment_pos=False) == ".":
            numeric_string += "."
            self._pos += 1

        while ch := self._read(increment_pos=False):
            if ch == "-":
                raise NUMERICS_INVALID_CHAR

            if ch == ".":
                if has_decimal:
                    raise NUMERICS_INVALID_CHAR
                has_decimal = True

                self._pos += 1
                numeric_string += ch
            elif ch.isnumeric():
                self._pos += 1
                numeric_string += ch
            elif _is_breakable(ch):
                break
            else:
                self._set_highlight_position()
                raise NUMERICS_INVALID_CHAR

        if numeric_string in (".", "-"):
            raise NUMERICS_INVALID_CHAR

        try:
            numeric_float = float(numeric_string)
        except ValueError as exc:
            raise UNREACHABLE from exc

        if (numeric_int := int(numeric_float)) == numeric_float:
            return Integer(value=numeric_int)

        return Float(value=numeric_float)

    def _parse_string(self, str_open_token: str) -> String:
        """
        Begin parsing a string, including the quotation value
        """
        self._set_highlight_position()
        string_value = ""

        if not _is_string_start_single_char(str_open_token) and not _is_string_start_multi_char(
            str_open_token
        ):
            raise UNREACHABLE

        while ch := self._read(increment_pos=False):
            if self._read(increment_pos=False, length=len(str_open_token)) == str_open_token:
                self._pos += len(str_open_token)
                return String(value=string_value)

            self._pos += 1
            string_value += ch

        raise STRINGS_NOT_CLOSED

    def _parse_function_arg(self, argument_parser: ParsedArgType) -> Argument:
        if self._read(increment_pos=False) == "%":
            self._pos += 1
            return self._parse_function()
        if _is_numeric_start(self._read(increment_pos=False)):
            return self._parse_numeric()
        if _is_boolean_true(self._read(increment_pos=False, length=4)):
            self._pos += 4
            return Boolean(value=True)
        if _is_boolean_false(self._read(increment_pos=False, length=5)):
            self._pos += 5
            return Boolean(value=False)
        if _is_null(self._read(increment_pos=False, length=4)):
            self._pos += 4
            return String(value="")
        if _is_string_start_multi_char(str_open_token := self._read(increment_pos=False, length=3)):
            self._pos += 3
            return self._parse_string(str_open_token)
        if _is_string_start_single_char(str_open_token := self._read(increment_pos=False)):
            self._pos += 1
            return self._parse_string(str_open_token)
        if self._read(increment_pos=False) == "[":
            self._pos += 1
            return self._parse_array()
        if self._read(increment_pos=False) == "{":
            self._pos += 1
            return self._parse_map()
        if _is_custom_function_argument_start(self._read(increment_pos=False)):
            self._pos += 1
            return self._parse_custom_function_argument()
        if _is_variable_start(self._read(increment_pos=False)):
            return self._parse_variable()

        self._set_highlight_position()
        raise _UNEXPECTED_CHAR_ARGUMENT(arg_type=argument_parser)

    def _parse_args(
        self, argument_parser: ParsedArgType, breaking_chars: str = ")"
    ) -> List[Argument]:
        """
        Begin parsing function args after the first ``(``, i.e. ``function_name(``
        """
        comma_count = 0
        arguments: List[Argument] = []
        while ch := self._read(increment_pos=False):
            if ch in breaking_chars:
                # i.e. ["arg", ] which is invalid
                if arguments and len(arguments) == comma_count:
                    raise _UNEXPECTED_COMMA_ARGUMENT(argument_parser)
                break

            if ch.isspace():
                self._pos += 1
            elif ch == ",":
                self._set_highlight_position()
                comma_count += 1
                if len(arguments) != comma_count:
                    raise _UNEXPECTED_COMMA_ARGUMENT(argument_parser)

                self._pos += 1
            else:
                arguments.append(self._parse_function_arg(argument_parser=argument_parser))

        return arguments

    def _parse_function(self) -> Function | Lambda:
        """
        Begin parsing a function after reading the first ``%``
        """
        function_name: str = ""
        function_args: Optional[List[Argument]] = None
        function_start_pos = self._pos

        while ch := self._read():
            if ch == ")":
                # Had '(' to indicate there are args
                if function_args is not None:
                    if self._name == function_name:
                        self._set_highlight_position(function_start_pos)
                        raise CycleDetected(
                            f"The custom function %{function_name} cannot call itself."
                        )

                    if Functions.is_built_in(function_name):
                        try:
                            return BuiltInFunction(
                                name=function_name, args=function_args
                            ).validate_args()
                        except IncompatibleFunctionArguments:
                            self._set_highlight_position(function_start_pos)
                            raise

                    # Is custom function
                    if (
                        self._custom_function_names is not None
                        and function_name not in self._custom_function_names
                    ):
                        self._set_highlight_position(function_start_pos)
                        raise FunctionDoesNotExist(
                            f"Function %{function_name} does not exist as a built-in or "
                            "custom function."
                        )

                    return CustomFunction(
                        name=function_name,
                        args=function_args,
                    )

                # Go back one so the parent function can close using the ')'
                self._pos -= 1
                return Lambda(value=function_name)

            if _is_function_name_char(ch):
                function_name += ch
            elif ch == "(":
                function_args = self._parse_args(argument_parser=ParsedArgType.FUNCTION)
            elif ch.isspace() or ch == ",":
                # function with no args, it's a lambda
                return Lambda(value=function_name)
            else:
                break

        self._set_highlight_position(pos=self._pos - 1)
        raise FUNCTION_INVALID_CHAR

    def _parse_array(self) -> UnresolvedArray:
        """
        Begin parsing an array after reading the first ``[``
        """
        function_args: List[Argument] = []

        while ch := self._read(increment_pos=False):
            if ch == "]":
                self._pos += 1
                return UnresolvedArray(value=function_args)

            function_args = self._parse_args(
                argument_parser=ParsedArgType.ARRAY, breaking_chars="]"
            )

        raise UNREACHABLE

    def _parse_map(self) -> UnresolvedMap:
        """
        Begin parsing a map after reading the first ``{``
        """
        output: Dict[Argument, Argument] = {}
        key: Optional[Argument] = None
        in_comma = False

        self._set_highlight_position()
        while ch := self._read(increment_pos=False):
            if ch == "}":
                if key is not None:
                    raise MAP_KEY_WITH_NO_VALUE  # key args are parsed immediately

                self._pos += 1
                return UnresolvedMap(value=output)

            if ch == ",":
                if in_comma:
                    raise _UNEXPECTED_COMMA_ARGUMENT(ParsedArgType.MAP_KEY)
                if key is not None:
                    raise MAP_KEY_WITH_NO_VALUE  # key args are parsed immediately
                if not output:
                    raise _UNEXPECTED_COMMA_ARGUMENT(ParsedArgType.MAP_KEY)
                in_comma = True
                self._pos += 1
            elif key is None:
                self._set_highlight_position()
                in_comma = False
                key_args = self._parse_args(
                    argument_parser=ParsedArgType.MAP_KEY, breaking_chars=":}"
                )

                if len(key_args) == 0 and self._read(increment_pos=False) == "}":
                    continue  # will return the map next iteration
                if len(key_args) == 0:
                    raise MAP_MISSING_KEY
                if len(key_args) > 1:
                    raise MAP_KEY_MULTIPLE_VALUES
                key = key_args[0]
            elif key is not None and ch == ":":
                self._set_highlight_position()
                self._pos += 1
                value_args = self._parse_args(
                    argument_parser=ParsedArgType.MAP_VALUE, breaking_chars=",}"
                )
                if len(value_args) == 0:
                    raise MAP_KEY_WITH_NO_VALUE
                if isinstance(key, NonHashable):
                    raise MAP_KEY_NOT_HASHABLE
                if isinstance(key, BuiltInFunction) and issubclass(key.output_type(), NonHashable):
                    raise MAP_KEY_NOT_HASHABLE
                if len(value_args) > 1:
                    raise MAP_KEY_MULTIPLE_VALUES

                output[key] = value_args[0]
                key = None
            else:
                break

        raise UNREACHABLE

    def _parse_main_loop(self, ch: str) -> bool:
        if ch == "\\" and self._read(increment_pos=False) in {"{", "}"}:
            # Escape brackets are \{ and \}, only add the second char
            self._literal_str += self._read()
            return True
        if ch == "}":
            if self._bracket_counter == 0:
                raise BRACKET_NOT_CLOSED

            del self._bracket_counter_pos_stack[-1]
            self._bracket_counter -= 1
            return True
        if ch == "{":
            self._bracket_counter_pos_stack.append(self._pos - 1)  # pos incremented when read
            self._bracket_counter += 1
            if self._literal_str:
                self._ast.append(String(value=self._literal_str))
                self._literal_str = ""

            # Allow whitespace after bracket opening
            while ch1 := self._read(increment_pos=False):
                if not ch1.isspace():
                    break
                self._pos += 1

            if ch1 is None:
                return False  # will hit closing bracket error

            if ch1 == "%":
                self._pos += 1
                self._ast.append(self._parse_function())
            elif ch1 == "[":
                self._pos += 1
                self._ast.append(self._parse_array())
            elif ch1 == "{":
                self._pos += 1
                self._ast.append(self._parse_map())
            elif _is_variable_start(ch1):
                self._ast.append(self._parse_variable())
            elif _is_numeric_start(ch1):
                raise NUMERICS_ONLY_ARGS
            elif (
                _is_string_start_single_char(ch1)
                or _is_string_start_multi_char(self._read(increment_pos=False, length=3))
                or _is_null(self._read(increment_pos=False, length=4))
            ):
                raise STRINGS_ONLY_ARGS
            elif _is_boolean_true(self._read(increment_pos=False, length=4)) or _is_boolean_false(
                self._read(increment_pos=False, length=5)
            ):
                raise BOOLEAN_ONLY_ARGS
            elif _is_custom_function_argument_start(self._read(increment_pos=False)):
                raise CUSTOM_FUNCTION_ARGUMENTS_ONLY_ARGS
            else:
                raise _UNEXPECTED_CHAR_ARGUMENT(arg_type=ParsedArgType.SCRIPT)
        elif self._bracket_counter == 0:
            # Only accumulate literal str if not in brackets
            self._literal_str += ch
        elif not ch.isspace():
            self._set_highlight_position(pos=self._pos - 1)
            raise BRACKET_INVALID_CHAR

        return True

    def _parse(self) -> SyntaxTree:

        while ch := self._read():
            continue_parse = self._parse_main_loop(ch)
            if not continue_parse:
                break

        if self._bracket_counter != 0:
            self._error_highlight_pos = self._bracket_counter_pos_stack[-1]
            raise BRACKET_NOT_CLOSED

        if self._literal_str:
            self._ast.append(String(value=self._literal_str))

        return SyntaxTree(ast=self._ast)


def parse(
    text: str,
    name: Optional[str] = None,
    custom_function_names: Optional[Set[str]] = None,
    variable_names: Optional[Set[str]] = None,
) -> SyntaxTree:
    """
    Entrypoint for parsing ytdl-sub code into a Syntax Tree
    """
    return _Parser(
        text=json.dumps(text) if not isinstance(text, str) else text,
        name=name,
        custom_function_names=custom_function_names,
        variable_names=variable_names,
    ).ast


# pylint: enable=invalid-name
