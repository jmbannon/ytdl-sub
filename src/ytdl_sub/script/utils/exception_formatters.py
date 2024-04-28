import sys
from typing import List
from typing import TypeVar

from ytdl_sub.script.types.resolvable import BuiltInFunctionType
from ytdl_sub.script.utils.exceptions import IncompatibleFunctionArguments
from ytdl_sub.script.utils.exceptions import UserException
from ytdl_sub.script.utils.type_checking import FunctionSpec
from ytdl_sub.script.utils.type_checking import is_union

UserExceptionT = TypeVar("UserExceptionT", bound=UserException)


class ParserExceptionFormatter:
    def __init__(self, text: str, start: int, end: int, exception: UserExceptionT):
        self._text = text
        self._start = start
        self._end = end
        self._exception = exception

    def _exception_text(self, border: int):
        """
        Format for single-line exceptions
        """
        text_left = max(0, self._start - border)
        text_right = min(len(self._text), self._start + border)
        relative_start = self._start - text_left

        exception_text: str = ""
        if text_left > 3:
            exception_text = "… "
            relative_start += len(exception_text)

        exception_text += self._text[text_left:text_right]

        if text_right < len(self._text) - 3:
            exception_text += " …"

        exception_text += "\n"
        exception_text += f"{' ' * relative_start}^"

        return "\n" + exception_text

    @property
    def _is_multi_line(self) -> bool:
        return "\n" in self._text

    def _exception_text_lines(self, border_lines: int = 0) -> str:
        """
        Format for multi-line exceptions
        """
        split_text = self._text.split("\n")

        start_line: int = sys.maxsize
        end_line: int = -1
        pos: int = 0
        for idx, line in enumerate(split_text):
            if self._start <= pos < self._end:
                start_line = min(start_line, idx)
                end_line = max(end_line, idx + 1)
            pos += len(line)

        true_start_line = start_line
        start_line = max(0, start_line - border_lines)
        end_line = min(len(split_text), end_line + border_lines)

        # Get min leading spaces between all lines to return
        min_leading_spaces = sys.maxsize
        for line in split_text[start_line:end_line]:
            min_leading_spaces = min(min_leading_spaces, len(line) - len(line.lstrip()))

        to_return: List[str] = []
        for idx in range(start_line, end_line):
            if idx == true_start_line:
                to_return.append(f">>> {split_text[idx][min_leading_spaces:]}")
            else:
                to_return.append(f"    {split_text[idx][min_leading_spaces:]}")

        return "\n" + "\n".join(to_return)

    def highlight(self) -> UserExceptionT:
        """
        Returns
        -------
        Exception with human-readable error highlighting for invalid syntax
        """
        if self._is_multi_line:
            invalid_syntax = self._exception_text_lines(border_lines=3)
        else:
            invalid_syntax = self._exception_text(border=20)

        return self._exception.__class__(f"{invalid_syntax}\n{str(self._exception)}")


class FunctionArgumentsExceptionFormatter:
    def __init__(
        self,
        input_spec: FunctionSpec,
        function_instance: BuiltInFunctionType,
    ):
        self._input_spec = input_spec
        self._name = function_instance.name
        self._input_args = function_instance.args

    def _received_args_str(self) -> str:
        received_type_names: List[str] = []
        for arg in self._input_args:
            if isinstance(arg, BuiltInFunctionType):
                if is_union(arg.output_type()):
                    readable_type_names = ", ".join(
                        sorted(type_.type_name() for type_ in arg.output_type().__args__)
                    )
                    received_type_names.append(f"%{arg.name}(...)->Union[{readable_type_names}]")
                else:
                    received_type_names.append(f"%{arg.name}(...)->{arg.output_type().type_name()}")
            else:
                received_type_names.append(arg.type_name())

        return f"({', '.join(name for name in received_type_names)})"

    def highlight(self) -> IncompatibleFunctionArguments:
        """
        Returns
        -------
        Exception with human-readable error highlighting for incompatible function arguments
        """
        return IncompatibleFunctionArguments(
            f"Incompatible arguments passed to function {self._name}.\n"
            f"Expected {self._input_spec.human_readable_input_args()}\n"
            f"Received {self._received_args_str()}"
        )
