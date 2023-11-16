from enum import Enum
from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.script.types.array import UnresolvedArray
from ytdl_sub.script.types.function import ArgumentType
from ytdl_sub.script.types.function import Function
from ytdl_sub.script.types.map import UnresolvedMap
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import NonHashable
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.types.variable import FunctionArgument
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exceptions import UNREACHABLE
from ytdl_sub.script.utils.exceptions import IncompatibleFunctionArguments
from ytdl_sub.script.utils.exceptions import InvalidSyntaxException
from ytdl_sub.script.utils.exceptions import UserException
from ytdl_sub.script.utils.parser_exception_formatter import ParserExceptionFormatter
from ytdl_sub.utils.exceptions import StringFormattingException
from ytdl_sub.validators.string_formatter_validators import is_valid_source_variable_name

# pylint: disable=invalid-name


class ArgumentParser(Enum):
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


def UNEXPECTED_CHAR_ARGUMENT(parser: ArgumentParser):
    return InvalidSyntaxException(f"Unexpected character when parsing {parser.value} arguments")


def UNEXPECTED_COMMA_ARGUMENT(parser: ArgumentParser):
    return InvalidSyntaxException(f"Unexpected comma when parsing {parser.value} arguments")


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


def _is_numeric_start(char: str) -> bool:
    return char.isnumeric() or char == "-"


def _is_string_start(char: str) -> bool:
    return char in ["'", '"']


def _is_breakable(char: str) -> bool:
    return char in ["}", ",", ")", "]"] or char.isspace()


def _is_boolean_true(string: Optional[str]) -> bool:
    return string == "True"


def _is_boolean_false(string: Optional[str]) -> bool:
    return string == "False"


class _Parser:
    def __init__(self, text: str):
        self._text = text
        self._pos = 0
        self._error_highlight_pos = 0
        self._ast: List[ArgumentType] = []

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
        while ch := self._read(increment_pos=False):
            if ch.isspace() and not var_name:
                self._pos += 1
                continue
            if _is_breakable(ch):
                break

            is_lower = ch.isascii() and ch.islower()
            if not var_name and not is_lower:
                raise StringFormattingException("invalid var name")

            if not (is_lower or ch.isnumeric() or ch == "_"):
                raise StringFormattingException("invalid var name")

            var_name += ch
            self._pos += 1

        if not var_name:
            raise StringFormattingException("invalid var name")

        assert is_valid_source_variable_name(var_name, raise_exception=False)
        return Variable(var_name)

    def _parse_custom_function_argument(self) -> FunctionArgument:
        """
        Begin parsing function args after the first ``$``, i.e. ``$1``
        """
        var_name = ""
        while ch := self._read(increment_pos=False):
            if ch.isspace() and not var_name:
                self._pos += 1
                continue
            if _is_breakable(ch):
                break

            is_numeric = ch.isnumeric()
            if not is_numeric:
                raise StringFormattingException("invalid function var name")

            var_name += ch
            self._pos += 1

        if not var_name:
            raise StringFormattingException("invalid var name")

        return FunctionArgument(name=f"${var_name}")

    def _parse_numeric(self) -> Integer | Float:
        numeric_string = ""

        if self._read(increment_pos=False) == "-":
            numeric_string += "-"
            self._pos += 1
        if has_decimal := (self._read(increment_pos=False) == "."):
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

    def _parse_string(self) -> String:
        """
        Begin parsing a string, including the quotation value
        """
        self._set_highlight_position()
        string_value = ""
        open_quotation_char = self._read()

        if not _is_string_start(open_quotation_char):
            raise UNREACHABLE

        is_escaped = False
        while ch := self._read():
            if ch == open_quotation_char and not is_escaped:
                return String(value=string_value)

            if ch == "\\" and not is_escaped:
                is_escaped = True
                continue

            string_value += ch
            is_escaped = False

        raise STRINGS_NOT_CLOSED

    def _parse_function_arg(self, argument_parser: ArgumentParser) -> ArgumentType:
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
        if _is_string_start(self._read(increment_pos=False)):
            return self._parse_string()
        if self._read(increment_pos=False) == "[":
            self._pos += 1
            return self._parse_array()
        if self._read(increment_pos=False) == "{":
            self._pos += 1
            return self._parse_map()
        if self._read(increment_pos=False) == "$":
            self._pos += 1
            return self._parse_custom_function_argument()
        if _is_variable_start(self._read(increment_pos=False)):
            return self._parse_variable()

        self._set_highlight_position()
        raise UNEXPECTED_CHAR_ARGUMENT(parser=argument_parser)

    def _parse_args(
        self, argument_parser: ArgumentParser, breaking_chars: str = ")"
    ) -> List[ArgumentType]:
        """
        Begin parsing function args after the first ``(``, i.e. ``function_name(``
        """
        comma_count = 0
        arguments: List[ArgumentType] = []
        while ch := self._read(increment_pos=False):
            if ch in breaking_chars:
                # i.e. ["arg", ] which is invalid
                if arguments and len(arguments) == comma_count:
                    raise UNEXPECTED_COMMA_ARGUMENT(argument_parser)
                break

            if ch.isspace():
                self._pos += 1
            elif ch == ",":
                self._set_highlight_position()
                comma_count += 1
                if len(arguments) != comma_count:
                    raise UNEXPECTED_COMMA_ARGUMENT(argument_parser)

                self._pos += 1
            else:
                arguments.append(self._parse_function_arg(argument_parser=argument_parser))

        return arguments

    def _parse_function(self) -> Function:
        """
        Begin parsing a function after reading the first ``%``
        """
        function_name: str = ""
        function_args: List[ArgumentType] = []
        function_start_pos = self._pos

        while ch := self._read():
            if ch == ")":
                try:
                    return Function.from_name_and_args(name=function_name, args=function_args)
                except IncompatibleFunctionArguments:
                    self._set_highlight_position(function_start_pos)
                    raise

            if ch != "(":
                function_name += ch
            else:
                function_args = self._parse_args(argument_parser=ArgumentParser.FUNCTION)

        raise StringFormattingException("Invalid function")

    def _parse_array(self) -> UnresolvedArray:
        """
        Begin parsing an array after reading the first ``[``
        """
        function_args: List[ArgumentType] = []

        while ch := self._read(increment_pos=False):
            if ch == "]":
                self._pos += 1
                return UnresolvedArray(value=function_args)

            function_args = self._parse_args(
                argument_parser=ArgumentParser.ARRAY, breaking_chars="]"
            )

        raise UNREACHABLE

    def _parse_map(self) -> UnresolvedMap:
        """
        Begin parsing a map after reading the first ``{``
        """
        output: Dict[ArgumentType, ArgumentType] = {}
        key: Optional[ArgumentType] = None
        in_comma = False

        self._set_highlight_position()
        while ch := self._read(increment_pos=False):
            if ch == "}":
                if key is not None:
                    raise MAP_KEY_WITH_NO_VALUE

                self._pos += 1
                return UnresolvedMap(value=output)
            elif ch == ",":
                if in_comma:
                    raise UNEXPECTED_COMMA_ARGUMENT(ArgumentParser.MAP_KEY)
                if key is not None:
                    raise MAP_KEY_WITH_NO_VALUE
                if not output:
                    raise UNEXPECTED_COMMA_ARGUMENT(ArgumentParser.MAP_KEY)
                in_comma = True
                self._pos += 1
            elif key is None:
                self._set_highlight_position()
                in_comma = False
                key_args = self._parse_args(
                    argument_parser=ArgumentParser.MAP_KEY, breaking_chars=":}"
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
                    argument_parser=ArgumentParser.MAP_VALUE, breaking_chars=",}"
                )
                if len(value_args) == 0:
                    raise MAP_KEY_WITH_NO_VALUE
                if isinstance(key, NonHashable):
                    raise MAP_KEY_NOT_HASHABLE
                if len(value_args) > 1:
                    raise UNREACHABLE

                output[key] = value_args[0]
                key = None
            else:
                raise UNREACHABLE

    def _parse(self) -> SyntaxTree:
        bracket_counter_pos_stack: List[int] = []
        bracket_counter = 0
        literal_str = ""
        while ch := self._read():
            if ch == "}":
                if bracket_counter == 0:
                    raise BRACKET_NOT_CLOSED

                del bracket_counter_pos_stack[-1]
                bracket_counter -= 1
                continue
            if ch == "{":
                bracket_counter_pos_stack.append(self._pos - 1)  # pos incremented when read
                bracket_counter += 1
                if literal_str:
                    self._ast.append(String(value=literal_str))
                    literal_str = ""

                # Allow whitespace after bracket opening
                while ch1 := self._read(increment_pos=False):
                    if not ch1.isspace():
                        break
                    self._pos += 1

                if ch1 is None:
                    raise StringFormattingException(
                        "Open bracket at the end was not properly closed"
                    )

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
                elif _is_string_start(ch1):
                    raise STRINGS_ONLY_ARGS
                elif _is_boolean_true(
                    self._read(increment_pos=False, length=4)
                ) or _is_boolean_false(self._read(increment_pos=False, length=5)):
                    raise BOOLEAN_ONLY_ARGS
                else:
                    raise UNEXPECTED_CHAR_ARGUMENT(parser=ArgumentParser.SCRIPT)
            elif bracket_counter == 0:
                # Only accumulate literal str if not in brackets
                literal_str += ch
            else:
                # Should only be possible to get here if it's a space
                assert ch.isspace()

        if bracket_counter != 0:
            self._error_highlight_pos = bracket_counter_pos_stack[-1]
            raise BRACKET_NOT_CLOSED

        if literal_str:
            self._ast.append(String(value=literal_str))

        return SyntaxTree(ast=self._ast)


def parse(text: str) -> SyntaxTree:
    return _Parser(text).ast


# pylint: enable=invalid-name
