from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.script.parser import parse
from ytdl_sub.script.syntax_tree import SyntaxTree
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.utils.exceptions import StringFormattingException


class OverridesResolver:
    def __init__(self, overrides: Dict[str, str]):
        self.overrides: Dict[Variable, SyntaxTree] = {
            Variable(name=name): parse(value) for name, value in overrides.items()
        }

    def _ensure_no_cycles(self) -> None:
        variable_dependencies: Dict[Variable, Set[Variable]] = {
            variable: ast.variables for variable, ast in self.overrides.items()
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

    def resolve_overrides(self) -> Dict[str, str]:
        self._ensure_no_cycles()

        unresolved_variables: List[Variable] = list(self.overrides.keys())
        resolved_variables: Dict[Variable, Resolvable] = {}

        while unresolved_variables:
            unresolved_count: int = len(unresolved_variables)

            for variable in unresolved_variables:
                if not self.overrides[variable].has_variable_dependency(
                    resolved_variables=resolved_variables
                ):
                    resolved_variables[variable] = self.overrides[variable].resolve(
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
