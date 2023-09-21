from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Resolvable


class SpecialFunctions:
    @staticmethod
    def if_(condition: Boolean, true: Resolvable, false: Resolvable) -> Resolvable:
        if condition.value:
            return true
        return false
