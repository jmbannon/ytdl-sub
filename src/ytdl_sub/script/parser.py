from contextlib import contextmanager
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
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.types.variable import FunctionArgument
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exceptions import InvalidSyntaxException
from ytdl_sub.utils.exceptions import StringFormattingException
from ytdl_sub.validators.string_formatter_validators import is_valid_source_variable_name

# pylint: disable=invalid-name


class _Parser:
    def __init__(self, text: str):
        self._text = text
        self._pos = 0
        self._ast: List[ArgumentType] = []

        self._syntax_tree = self._parse()

    @property
    def ast(self) -> SyntaxTree:
        """
        Returns
        -------
        Abstract syntax tree of the parsed text
        """
        return self._syntax_tree

    @contextmanager
    def _error_formatting(self) -> None:
        parked_pos = self._pos
        try:
            yield
        except InvalidSyntaxException as exc:
            border = 4
            text_left = max(0, parked_pos - border)
            text_right = min(len(self._text), self._pos + border)
            text_len = text_right - text_left

            raise InvalidSyntaxException(
                "Invalid syntax:\n"
                f"  {self._text[text_left:text_right]}\n"
                f"  {' ' * border}{'^' * text_len}\n\n"
                f"{str(exc)}"
            ) from exc

    def _read(self, increment_pos: bool = True, length: int = 1) -> Optional[str]:
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
            if ch in ["}", ",", ")", "]"] or ch.isspace():
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

    def _parse_function_argument(self) -> FunctionArgument:
        """
        Begin parsing function args after the first ``$``, i.e. ``$1``
        """
        var_name = ""
        while ch := self._read(increment_pos=False):
            if ch.isspace() and not var_name:
                self._pos += 1
                continue
            if ch in ["}", ",", ")", "]"] or ch.isspace():
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
        while ch := self._read(increment_pos=False):
            if not (ch.isnumeric() or ch == "."):
                break

            self._pos += 1
            numeric_string += ch

        try:
            numeric_float = float(numeric_string)
        except ValueError:
            raise StringFormattingException(f"Invalid numeric: {numeric_string}")

        if (numeric_int := int(numeric_float)) == numeric_float:
            return Integer(value=numeric_int)

        return Float(value=numeric_float)

    def _parse_string(self) -> String:
        """
        Begin parsing a string, including the quotation value
        """
        string_value = ""
        open_quotation_char = self._read()
        assert open_quotation_char in ["'", '"']

        while ch := self._read():
            if ch == open_quotation_char:
                return String(value=string_value)
            string_value += ch

        raise StringFormattingException("String not closed")

    def _parse_function_arg(self) -> ArgumentType:
        if self._read(increment_pos=False) == "%":
            self._pos += 1
            return self._parse_function()
        if self._read(increment_pos=False).isnumeric():
            return self._parse_numeric()
        if (self._read(increment_pos=False, length=4) or "").lower() == "true":
            self._pos += 4
            return Boolean(value=True)
        if (self._read(increment_pos=False, length=5) or "").lower() == "false":
            self._pos += 5
            return Boolean(value=False)
        if self._read(increment_pos=False) in ["'", '"']:
            return self._parse_string()
        if self._read(increment_pos=False) == "[":
            self._pos += 1
            return self._parse_array()
        if self._read(increment_pos=False) == "{":
            self._pos += 1
            return self._parse_map()
        if self._read(increment_pos=False) == "$":
            self._pos += 1
            return self._parse_function_argument()
        if self._read(increment_pos=False).isascii() and self._read(increment_pos=False).islower():
            return self._parse_variable()
        raise StringFormattingException(
            "Invalid function argument, should be either a function, int, float, "
            "string, boolean, or variable without brackets"
        )

    def _parse_args(self, breaking_chars: str = ")") -> List[ArgumentType]:
        """
        Begin parsing function args after the first ``(``, i.e. ``function_name(``
        """
        argument_index = 0
        comma_count = 0

        arguments: List[ArgumentType] = []
        while ch := self._read(increment_pos=False):
            if ch in breaking_chars:
                break

            if ch.isspace():
                self._pos += 1
            elif ch == ",":
                comma_count += 1
                if argument_index != comma_count:
                    raise StringFormattingException("Comma argument shenanigans")

                self._pos += 1
            else:
                argument_index += 1
                arguments.append(self._parse_function_arg())

        return arguments

    def _parse_function(self) -> Function:
        """
        Begin parsing a function after reading the first ``%``
        """
        function_name: str = ""
        function_args: List[ArgumentType] = []

        while ch := self._read():
            if ch == ")":
                return Function.from_name_and_args(name=function_name, args=function_args)

            if ch != "(":
                function_name += ch
            else:
                function_args = self._parse_args()

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
            else:
                function_args = self._parse_args(breaking_chars="]")

        raise StringFormattingException("Invalid function")

    def _parse_map(self) -> UnresolvedMap:
        """
        Begin parsing a map after reading the first ``{``
        """
        output: Dict[ArgumentType, ArgumentType] = {}
        key: Optional[ArgumentType] = None
        in_comma = False

        with self._error_formatting():
            while ch := self._read(increment_pos=False):
                if ch == "}":
                    if key is not None:
                        raise InvalidSyntaxException("Map has a key with no value")

                    self._pos += 1
                    return UnresolvedMap(value=output)
                elif ch == ",":
                    if in_comma:
                        raise StringFormattingException("Comma followed by comma")
                    if key is not None:
                        raise InvalidSyntaxException("Map has a key with no value")
                    if output is None:
                        raise StringFormattingException("Empty dict with comma")
                    in_comma = True
                    self._pos += 1
                elif key is None:
                    in_comma = False
                    key_args = self._parse_args(breaking_chars=":")
                    if len(key_args) != 1:
                        raise StringFormattingException("Lazy parsing but got mlutiple args")
                    key = key_args[0]
                elif key is not None and ch == ":":
                    self._pos += 1
                    value_args = self._parse_args(breaking_chars=",}")
                    if len(value_args) != 1:
                        raise InvalidSyntaxException("Map has a key with no value")

                    output[key] = value_args[0]
                    key = None
                else:
                    raise StringFormattingException("Invalid map")

    def _parse(self) -> SyntaxTree:
        bracket_counter = 0
        literal_str = ""
        while ch := self._read():
            if ch == "}":
                bracket_counter -= 1
                continue
            if ch == "{":
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
                else:
                    self._ast.append(self._parse_variable())
            elif bracket_counter == 0:
                # Only accumulate literal str if not in brackets
                literal_str += ch
            else:
                # Should only be possible to get here if it's a space
                assert ch.isspace()

        if bracket_counter != 0:
            raise StringFormattingException("Bracket count mismatch")

        if literal_str:
            self._ast.append(String(value=literal_str))

        return SyntaxTree(ast=self._ast)


def parse(text: str) -> SyntaxTree:
    return _Parser(text).ast


# pylint: enable=invalid-name
