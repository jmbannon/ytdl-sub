import sys
from typing import List

from ytdl_sub.script.utils.exceptions import InvalidSyntaxException


class ParserExceptionFormatter:
    def __init__(self, text: str, start: int, end: int, exception: InvalidSyntaxException):
        self._text = text
        self._start = start
        self._end = end
        self._exception = exception

    def exception_text(self, border: int):
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
    def is_multi_line(self) -> bool:
        return "\n" in self._text

    def exception_text_lines(self, border_lines: int = 0) -> str:
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

    def highlight(self) -> InvalidSyntaxException:
        if self.is_multi_line:
            invalid_syntax = self.exception_text_lines(border_lines=3)
        else:
            invalid_syntax = self.exception_text(border=20)

        return InvalidSyntaxException(f"{invalid_syntax}\n{str(self._exception)}")
