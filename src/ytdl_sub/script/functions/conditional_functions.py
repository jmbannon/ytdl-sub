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
        :description:
          Conditional ``if`` statement that returns the ``true`` or ``false`` parameter
          depending on the ``condition`` value.
        """
        if condition.value:
            return true
        return false

    @staticmethod
    def if_passthrough(
        maybe_true_arg: ReturnableArgumentA, else_arg: ReturnableArgumentB
    ) -> Union[ReturnableArgumentA, ReturnableArgumentB]:
        """
        :description:
          Conditional ``if`` statement that returns the ``maybe_true_arg`` if it evaluates to True,
          otherwise returns ``else_arg``.
        """
        if bool(maybe_true_arg.value):
            return maybe_true_arg
        return else_arg
