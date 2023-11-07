from typing import Union

from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import Resolvable_1
from ytdl_sub.script.types.resolvable import Resolvable_2


class SpecialFunctions:
    @staticmethod
    def if_(
        condition: Boolean, true: Resolvable, false: Resolvable
    ) -> Union[Resolvable_1, Resolvable_2]:
        if condition.value:
            return true
        return false
