from dataclasses import dataclass
from queue import LifoQueue
from typing import Optional, List

from ytdl_sub.validators.string_formatter_validators import is_valid_source_variable_name

@dataclass
class Variable:
    name: str

@dataclass
class Function:
    name: str
    args: List[str]


class Parser:

    def __init__(self, text: str):
        self._text = text
        self._pos = 0
        self._stack: LifoQueue[Variable | Function] = LifoQueue()

    def read(self) -> Optional[str]:
        try:
            ch = self._text[self._pos]
        except IndexError:
            return None

        self._pos += 1
        return ch

    def parse_variable(self) -> Variable:
        var_name = ""
        while ch := self.read():
            if ch == "}":
                break
            var_name += ch

        _ = is_valid_source_variable_name(var_name, raise_exception=True)
        return Variable(var_name)

    def parse_function(self) -> Function:
        parenthesis_counter = 0
        func_name = ""
        func_args = ""

        while ch := self.read():
            if ch not in ['(', ')']:
                if parenthesis_counter > 0:
                    func_args += ch
                else:
                    func_name += ch
            elif ch == '(':
                parenthesis_counter += 1
            elif ch == ')':
                parenthesis_counter -= 1
                if parenthesis_counter == 0:
                    break







    def parse(self):
        while True:
            ch = self.read()
            if ch == '{':
                self.parse_variable()
            if ch == '%':
                self.parse_function()


