import functools
import inspect
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from inspect import FullArgSpec
from typing import Callable
from typing import Dict
from typing import List
from typing import Set
from typing import Type
from typing import Union
from typing import final

from ytdl_sub.script.functions import Functions
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.utils.exceptions import StringFormattingException

ArgumentType = Union[Integer, Float, String, Boolean, Variable, "Function"]


@dataclass(frozen=True)
class VariableDependency(ABC):
    @property
    @abstractmethod
    def variables(self) -> Set[Variable]:
        raise NotImplemented()

    @abstractmethod
    def resolve(self, resolved_variables: Dict[Variable, Resolvable]) -> str:
        raise NotImplemented()

    @final
    def has_variable_dependency(self, resolved_variables: Dict[Variable, Resolvable]) -> bool:
        """
        Returns
        -------
        True if variable dependency. False otherwise.
        """
        return self.variables.issubset(set(resolved_variables.keys()))


@dataclass(frozen=True)
class Function(VariableDependency):
    name: str
    args: List[ArgumentType]

    def __post_init__(self):
        # TODO: Figure out resolution via introspecting args and outputs of function
        if len(self.args) != len(self.input_types):
            raise StringFormattingException(
                f"Unequal amount of arguments passed to function {self.name}.\n"
                f"{self._expected_received_error_msg()}"
            )

        for input_arg, input_arg_type in zip(self.args, self.input_types):
            if isinstance(input_arg, Function):
                input_arg = input_arg.output_type
            elif isinstance(input_arg, Variable):
                pass  # cannot evaluate the variable yet, so pass
            if not issubclass(input_arg.__class__, input_arg_type):
                raise StringFormattingException(
                    f"Invalid arguments passed to function {self.name}.\n"
                    f"{self._expected_received_error_msg()}"
                )

    def _expected_received_error_msg(self) -> str:
        output_type_names: List[str] = []
        for arg in self.args:
            if isinstance(arg, Function):
                output_type_names.append(f"{arg.name}(...)->{arg.output_type.__name__}")
            else:
                output_type_names.append(arg.__class__.__name__)

        return (
            f"Expected ({', '.join([type_.__name__ for type_ in self.input_types])}).\n"
            f"Received ({', '.join([output_type_name for output_type_name in output_type_names])})"
        )

    @property
    def callable(self) -> Callable[..., Resolvable]:
        try:
            return getattr(Functions, self.name)
        except AttributeError:
            raise StringFormattingException(f"Function name {self.name} does not exist")

    @functools.cached_property
    def arg_spec(self) -> FullArgSpec:
        return inspect.getfullargspec(self.callable)

    @property
    def input_types(self) -> List[Type[Resolvable]]:
        return [self.arg_spec.annotations[arg_name] for arg_name in self.arg_spec.args]

    @property
    def output_type(self) -> Type[Resolvable]:
        return self.arg_spec.annotations["return"]

    @property
    def variables(self) -> Set[Variable]:
        """
        Returns
        -------
        All variables used within the function
        """
        variables: Set[Variable] = set()
        for arg in self.args:
            if isinstance(arg, Variable):
                variables.add(arg)
            elif isinstance(arg, Function):
                variables.update(arg.variables)

        return variables

    def resolve(self, resolved_variables: Dict[Variable, Resolvable]) -> Resolvable:
        raise NotImplemented()
