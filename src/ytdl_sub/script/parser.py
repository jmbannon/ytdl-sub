from dataclasses import dataclass
from queue import LifoQueue
from typing import List
from typing import Optional
from typing import Union

from ytdl_sub.utils.exceptions import StringFormattingException
from ytdl_sub.validators.string_formatter_validators import is_valid_source_variable_name

# pylint: disable=invalid-name


@dataclass(frozen=True)
class Integer:
    value: int


@dataclass(frozen=True)
class Float:
    value: float


@dataclass(frozen=True)
class Boolean:
    value: bool


@dataclass(frozen=True)
class String:
    value: str


@dataclass(frozen=True)
class Variable:
    name: str


NumericType = Union[Integer, Float]
ArgumentType = Union[Integer, Float, String, Boolean, Variable, "Function"]


@dataclass(frozen=True)
class Function:
    name: str
    args: List[ArgumentType]


@dataclass(frozen=True)
class LiteralString:
    value: str


class Parser:
    def __init__(self, text: str):
        self._text = text
        self._pos = 0
        self._stack: LifoQueue[LiteralString | Variable | Function] = LifoQueue()

    def read(self, increment_pos: bool = True, length: int = 1) -> Optional[str]:
        try:
            ch = self._text[self._pos : (self._pos + length)]
        except IndexError:
            return None

        if increment_pos:
            self._pos += length
        return ch

    def parse_variable(self) -> Variable:
        var_name = ""
        while ch := self.read(increment_pos=False):
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

        assert is_valid_source_variable_name(var_name, raise_exception=False)
        return Variable(var_name)

    def parse_numeric(self) -> NumericType:
        numeric_string = ""
        while ch := self.read(increment_pos=False):
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

    def parse_string(self) -> String:
        """
        Begin parsing a string, including the quotation value
        """
        string_value = ""
        open_quotation_char = self.read()
        assert open_quotation_char in ["'", '"']

        while ch := self.read():
            if ch == open_quotation_char:
                return String(value=string_value)
            string_value += ch

        raise StringFormattingException("String not closed")

    def parse_function_arg(self) -> ArgumentType:
        if self.read(increment_pos=False) == "%":
            self._pos += 1
            return self.parse_function()
        if self.read(increment_pos=False).isnumeric():
            return self.parse_numeric()
        if (self.read(increment_pos=False, length=4) or "").lower() == "true":
            self._pos += 4
            return Boolean(value=True)
        if (self.read(increment_pos=False, length=5) or "").lower() == "false":
            self._pos += 5
            return Boolean(value=False)
        if self.read(increment_pos=False) in ["'", '"']:
            return self.parse_string()
        if self.read(increment_pos=False).isascii() and self.read(increment_pos=False).islower():
            return self.parse_variable()
        raise StringFormattingException(
            "Invalid function argument, should be either a function, int, float, "
            "string, boolean, or variable without brackets"
        )

    def parse_function_args(self) -> List[ArgumentType]:
        """
        Begin parsing function args after the first ``(``, i.e. ``function_name(``
        """
        argument_index = 0
        comma_count = 0

        arguments: List[ArgumentType] = []
        while ch := self.read(increment_pos=False):
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
                arguments.append(self.parse_function_arg())

        return arguments

    def parse_function(self) -> Function:
        """
        Begin parsing a function after reading the first ``%``
        """
        function_name: str = ""
        function_args: List[String | Variable | "Function"] = []

        while ch := self.read():
            if ch == ")":
                return Function(name=function_name, args=function_args)

            if ch != "(":
                function_name += ch
            else:
                function_args = self.parse_function_args()

        raise StringFormattingException("Invalid function")

    def parse(self) -> "Parser":
        bracket_counter = 0
        literal_str = ""
        while ch := self.read():
            if ch == "}":
                bracket_counter -= 1
                break
            if ch == "{":
                bracket_counter += 1
                if literal_str:
                    self._stack.put(LiteralString(literal_str))
                    literal_str = ""

                # Allow whitespace after bracket opening
                while ch1 := self.read(increment_pos=False):
                    if not ch1.isspace():
                        break
                    self._pos += 1

                if ch1 is None:
                    raise StringFormattingException(
                        "Open bracket at the end was not properly closed"
                    )

                if ch1 == "%":
                    self._pos += 1
                    self._stack.put(self.parse_function())
                else:
                    self._stack.put(self.parse_variable())
            else:
                literal_str += ch

        if bracket_counter != 0:
            raise StringFormattingException("Bracket count mismatch")

        if literal_str:
            self._stack.put(LiteralString(literal_str))

        return self


# pylint: enable=invalid-name
