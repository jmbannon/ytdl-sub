from typing import List
from typing import Optional

from ytdl_sub.script.functions import Boolean
from ytdl_sub.script.functions import Float
from ytdl_sub.script.functions import Integer
from ytdl_sub.script.functions import String
from ytdl_sub.script.types import ArgumentType
from ytdl_sub.script.types import Function
from ytdl_sub.script.types import SyntaxTree
from ytdl_sub.script.types import Variable
from ytdl_sub.utils.exceptions import StringFormattingException
from ytdl_sub.validators.string_formatter_validators import is_valid_source_variable_name

# pylint: disable=invalid-name


class _Parser:
    def __init__(self, text: str):
        self._text = text
        self._pos = 0
        self._ast: List[String | Variable | Function] = []

        self._syntax_tree = self._parse()

    @property
    def ast(self) -> SyntaxTree:
        """
        Returns
        -------
        Abstract syntax tree of the parsed text
        """
        return self._syntax_tree

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
            if ch in ["}", ","] or ch.isspace():
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
        if self._read(increment_pos=False).isascii() and self._read(increment_pos=False).islower():
            return self._parse_variable()
        raise StringFormattingException(
            "Invalid function argument, should be either a function, int, float, "
            "string, boolean, or variable without brackets"
        )

    def _parse_function_args(self) -> List[ArgumentType]:
        """
        Begin parsing function args after the first ``(``, i.e. ``function_name(``
        """
        argument_index = 0
        comma_count = 0

        arguments: List[ArgumentType] = []
        while ch := self._read(increment_pos=False):
            if ch == ")":
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
        function_args: List[String | Variable | "Function"] = []

        while ch := self._read():
            if ch == ")":
                return Function(name=function_name, args=function_args)

            if ch != "(":
                function_name += ch
            else:
                function_args = self._parse_function_args()

        raise StringFormattingException("Invalid function")

    def _parse(self) -> SyntaxTree:
        bracket_counter = 0
        literal_str = ""
        while ch := self._read():
            if ch == "}":
                bracket_counter -= 1
                break
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
                else:
                    self._ast.append(self._parse_variable())
            else:
                literal_str += ch

        if bracket_counter != 0:
            raise StringFormattingException("Bracket count mismatch")

        if literal_str:
            self._ast.append(String(value=literal_str))

        return SyntaxTree(ast=self._ast)


def parse(text: str) -> SyntaxTree:
    return _Parser(text).ast


# pylint: enable=invalid-name
