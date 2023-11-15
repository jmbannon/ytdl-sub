from typing import Union

from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import AnyType_1
from ytdl_sub.script.types.resolvable import AnyType_2


class SpecialFunctions:
    @staticmethod
    def if_(
        condition: Boolean, true: AnyType_1, false: AnyType_2
    ) -> Union[AnyType_1, AnyType_2]:
        if condition.value:
            return true
        return false
