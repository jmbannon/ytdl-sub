from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict
from typing import Iterable
from typing import List
from typing import Set
from typing import final

from ytdl_sub.script.types.resolvable import Argument
from ytdl_sub.script.types.resolvable import FunctionType
from ytdl_sub.script.types.resolvable import Lambda
from ytdl_sub.script.types.resolvable import NamedCustomFunction
from ytdl_sub.script.types.resolvable import ParsedCustomFunction
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.variable import FunctionArgument
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exceptions import UNREACHABLE


@dataclass(frozen=True)
class VariableDependency(ABC):
    @property
    @abstractmethod
    def _iterable_arguments(self) -> List[Argument]:
        pass

    @final
    @property
    def variables(self) -> Set[Variable]:
        output: Set[Variable] = set()
        for arg in self._iterable_arguments:
            if isinstance(arg, Variable):
                output.add(arg)
            if isinstance(arg, VariableDependency):
                output.update(arg.variables)

        return output

    @final
    @property
    def function_arguments(self) -> Set[FunctionArgument]:
        output: Set[FunctionArgument] = set()
        for arg in self._iterable_arguments:
            if isinstance(arg, FunctionArgument):
                output.add(arg)
            if isinstance(arg, VariableDependency):
                output.update(arg.function_arguments)

        return output

    @final
    @property
    def lambda_arguments(self) -> Set[Lambda]:
        output: Set[Lambda] = set()
        for arg in self._iterable_arguments:
            if isinstance(arg, Lambda):
                output.add(arg)
            if isinstance(arg, VariableDependency):
                output.update(arg.lambda_arguments)

        return output

    @final
    @property
    def custom_functions(self) -> Set[ParsedCustomFunction]:
        output: Set[ParsedCustomFunction] = set()
        for arg in self._iterable_arguments:
            if isinstance(arg, NamedCustomFunction):
                if not isinstance(arg, FunctionType):
                    # A NamedCustomFunction should also always be a FunctionType
                    raise UNREACHABLE

                # Custom funcs aren't hashable, so recreate just the base-class portion
                output.add(ParsedCustomFunction(name=arg.name, num_input_args=len(arg.args)))
            if isinstance(arg, VariableDependency):
                output.update(arg.custom_functions)

        return output

    @abstractmethod
    def resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, "VariableDependency"],
    ) -> Resolvable:
        pass

    @classmethod
    def _resolve_argument_type(
        cls,
        arg: Argument,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, "VariableDependency"],
    ) -> Resolvable:
        if isinstance(arg, Resolvable):
            return arg
        if isinstance(arg, Variable):
            if arg not in resolved_variables:
                # All variables should exist and be resolved at this point
                raise UNREACHABLE
            return resolved_variables[arg]
        if isinstance(arg, VariableDependency):
            return arg.resolve(
                resolved_variables=resolved_variables, custom_functions=custom_functions
            )

        raise UNREACHABLE

    @final
    def is_subset_of(self, variables: Iterable[Variable]) -> bool:
        """
        Returns
        -------
        True if variable dependency. False otherwise.
        """
        return not self.variables.issubset(variables)

    @final
    def contains(self, variables: Iterable[Variable]) -> bool:
        return len(self.variables.intersection(variables)) > 0
