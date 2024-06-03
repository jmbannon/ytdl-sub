from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict
from typing import Iterable
from typing import List
from typing import Set
from typing import Type
from typing import TypeVar
from typing import final

from ytdl_sub.script.types.resolvable import Argument
from ytdl_sub.script.types.resolvable import BuiltInFunctionType
from ytdl_sub.script.types.resolvable import FunctionType
from ytdl_sub.script.types.resolvable import Lambda
from ytdl_sub.script.types.resolvable import NamedCustomFunction
from ytdl_sub.script.types.resolvable import ParsedCustomFunction
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.variable import FunctionArgument
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exceptions import UNREACHABLE

TypeT = TypeVar("TypeT")


@dataclass(frozen=True)
class VariableDependency(ABC):
    @property
    @abstractmethod
    def _iterable_arguments(self) -> List[Argument]:
        """
        Returns
        -------
        Any arguments in the VariableDependency that may or may not need to be resolved.
        """

    def _recurse_get(
        self, ttype: Type[TypeT], subclass: bool = False, instance: bool = True
    ) -> List[TypeT]:
        output: List[TypeT] = []
        for arg in self._iterable_arguments:
            if subclass and issubclass(type(arg), ttype):
                output.append(arg)
            elif instance and isinstance(arg, ttype):
                output.append(arg)
            elif type(arg) == ttype:  # pylint: disable=unidiomatic-typecheck
                output.append(arg)

            if isinstance(arg, VariableDependency):
                # pylint: disable=protected-access
                output.extend(arg._recurse_get(ttype, subclass=subclass, instance=instance))
                # pylint: enable=protected-access

        return output

    @final
    @property
    def variables(self) -> Set[Variable]:
        """
        Returns
        -------
        All Variables that this depends on.
        """
        return set(self._recurse_get(Variable, instance=False))

    @final
    @property
    def built_in_functions(self) -> List[BuiltInFunctionType]:
        """
        Returns
        -------
        All BuiltInFunctions that this depends on.
        """
        return self._recurse_get(BuiltInFunctionType)

    @final
    @property
    def function_arguments(self) -> Set[FunctionArgument]:
        """
        Returns
        -------
        All FunctionArguments that this depends on.
        """
        return set(self._recurse_get(FunctionArgument))

    @final
    @property
    def lambdas(self) -> Set[Lambda]:
        """
        Returns
        -------
        All Lambdas that this depends on.
        """
        return set(self._recurse_get(Lambda, subclass=True))

    # pylint: disable=missing-raises-doc

    @final
    @property
    def custom_functions(self) -> Set[ParsedCustomFunction]:
        """
        Returns
        -------
        All CustomFunctions that this depends on.
        """
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

    # pylint: enable=missing-raises-doc

    @abstractmethod
    def resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, "VariableDependency"],
    ) -> Resolvable:
        """
        Parameters
        ----------
        resolved_variables
            Lookup of variables that have been resolved
        custom_functions
            Lookup of any custom functions that have been parsed

        Returns
        -------
        Resolved value
        """

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
    def is_subset_of(
        self,
        variables: Iterable[Variable],
        custom_function_definitions: Dict[str, "VariableDependency"],
    ) -> bool:
        """
        Returns
        -------
        True if it contains all input variables as a dependency. False otherwise.
        """
        for custom_function in self.custom_functions:
            if custom_function_definitions[custom_function.name].is_subset_of(
                variables=variables, custom_function_definitions=custom_function_definitions
            ):
                return True

        return not self.variables.issubset(variables)

    @final
    def contains(
        self,
        variables: Iterable[Variable],
        custom_function_definitions: Dict[str, "VariableDependency"],
    ) -> bool:
        """
        Returns
        -------
        True if it contains any of the input variables. False otherwise.
        """
        for custom_function in self.custom_functions:
            if custom_function_definitions[custom_function.name].contains(
                variables=variables, custom_function_definitions=custom_function_definitions
            ):
                return True
        return len(self.variables.intersection(variables)) > 0
