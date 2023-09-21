from typing import TypeVar

from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Resolvable

ResolvableTrue = TypeVar("ResolvableTrue", bound=Resolvable)
ResolvableFalse = TypeVar("ResolvableFalse", bound=Resolvable)


class ConditionalFunctions:
    @staticmethod
    def iff(
        condition: Boolean, true: ResolvableTrue, false: ResolvableFalse
    ) -> ResolvableTrue | ResolvableFalse:
        if condition.value:
            return true
        return false
