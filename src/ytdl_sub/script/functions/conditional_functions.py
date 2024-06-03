from typing import Union

from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import ReturnableArgumentA
from ytdl_sub.script.types.resolvable import ReturnableArgumentB
from ytdl_sub.script.utils.exceptions import FunctionRuntimeException


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
            return true.value()
        return false.value()

    @staticmethod
    def elif_(*if_elif_else: AnyArgument) -> AnyArgument:
        """
        :description:
          Conditional ``if`` statement that is capable of doing else-ifs (``elif``) via
          adjacent arguments. It is expected for there to be an odd number of arguments >= 3 to
          supply at least one conditional and an else.
        :usage:

          .. code-block:: python

             %elif(
                condition1,
                return1,
                condition2,
                return2,
                ...
                else_return
             )
        """
        arguments = list(if_elif_else)
        if len(arguments) < 3:
            raise FunctionRuntimeException("elif requires at least 3 arguments")

        if len(arguments) % 2 == 0:
            raise FunctionRuntimeException("elif must have an odd number of arguments")

        for idx in range(0, len(arguments) - 1, 2):
            if bool(arguments[idx].value):
                return arguments[idx + 1].value()

        return arguments[-1].value()

    @staticmethod
    def if_passthrough(
        maybe_true_arg: ReturnableArgumentA, else_arg: ReturnableArgumentB
    ) -> Union[ReturnableArgumentA, ReturnableArgumentB]:
        """
        :description:
          Conditional ``if`` statement that returns the ``maybe_true_arg`` if it evaluates to True,
          otherwise returns ``else_arg``.
        """
        maybe_true_value = maybe_true_arg.value()
        if bool(maybe_true_value.value):
            return maybe_true_value
        return else_arg.value()
