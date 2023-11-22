from typing import Union

from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import ReturnableArgumentA
from ytdl_sub.script.types.resolvable import ReturnableArgumentB


class ConditionalFunctions:
    @staticmethod
    def if_(
        condition: Boolean, true: ReturnableArgumentA, false: ReturnableArgumentB
    ) -> Union[ReturnableArgumentA, ReturnableArgumentB]:
        """
        Conditional ``if`` statement that returns the ``true`` or ``false`` parameter
        depending on the ``condition`` value.
        """
        if condition.value:
            return true
        return false
