from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.script.types.function import Function
from ytdl_sub.script.types.function import VariableDependency
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.utils.exceptions import StringFormattingException


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
