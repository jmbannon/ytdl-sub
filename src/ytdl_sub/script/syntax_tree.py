from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union
from typing import final

from ytdl_sub.script.functions import Boolean
from ytdl_sub.script.functions import Float
from ytdl_sub.script.functions import Functions
from ytdl_sub.script.functions import Integer
from ytdl_sub.script.functions import Resolvable
from ytdl_sub.script.functions import String
from ytdl_sub.utils.exceptions import StringFormattingException


@dataclass(frozen=True)
class Variable:
    name: str


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
        try:
            getattr(Functions, self.name)
        except AttributeError:
            raise StringFormattingException(f"Function name {self.name} does not exist")

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


@dataclass(frozen=True)
class SyntaxTree(VariableDependency):
    ast: List[String | Variable | Function]

    @property
    def variables(self) -> Set[Variable]:
        """
        Returns
        -------
        All variables used within the SyntaxTree
        """
        variables: Set[Variable] = set()
        for token in self.ast:
            if isinstance(token, Variable):
                variables.add(token)
            elif isinstance(token, Function):
                variables.update(token.variables)

        return variables

    def resolve(self, resolved_variables: Dict[Variable, Resolvable]) -> Resolvable:
        output: str = ""
        for token in self.ast:
            if isinstance(token, String):
                output += token.resolve()
            elif isinstance(token, Variable):
                output += resolved_variables[token].resolve()
            elif isinstance(token, Function):
                output += token.resolve(resolved_variables=resolved_variables)
            else:
                assert False, "should never reach"

        return String(output)

    @classmethod
    def detect_cycles(cls, parsed_overrides: Dict[str, "SyntaxTree"]) -> None:
        """
        Parameters
        ----------
        parsed_overrides
            ``overrides`` in a subscription, parsed into a SyntaxTree
        """
        variable_dependencies: Dict[Variable, Set[Variable]] = {
            Variable(name): ast.variables for name, ast in parsed_overrides.items()
        }

        def _traverse(
            to_variable: Variable, visited_variables: Optional[List[Variable]] = None
        ) -> None:
            if visited_variables is None:
                visited_variables = []

            if to_variable in visited_variables:
                raise StringFormattingException("Detected cycle in variables")
            visited_variables.append(to_variable)

            for dep in variable_dependencies[to_variable]:
                _traverse(to_variable=dep, visited_variables=visited_variables)

        for variable in variable_dependencies.keys():
            _traverse(variable)

    @classmethod
    def resolve_overrides(cls, parsed_overrides: Dict[str, "SyntaxTree"]) -> Dict[str, str]:
        cls.detect_cycles(parsed_overrides=parsed_overrides)

        overrides: Dict[Variable, "SyntaxTree"] = {
            Variable(name): ast for name, ast in parsed_overrides.items()
        }

        unresolved_variables: List[Variable] = list(overrides.keys())
        resolved_variables: Dict[Variable, Resolvable] = {}

        while unresolved_variables:
            unresolved_count: int = len(unresolved_variables)

            for variable in unresolved_variables:
                if not overrides[variable].has_variable_dependency(
                    resolved_variables=resolved_variables
                ):
                    resolved_variables[variable] = overrides[variable].resolve(
                        resolved_variables=resolved_variables
                    )
                    unresolved_variables.remove(variable)

            assert (
                len(unresolved_variables) != unresolved_count
            ), "did not resolve any variables, cycle detected"

        return {
            variable.name: resolvable.resolve()
            for variable, resolvable in resolved_variables.items()
        }
