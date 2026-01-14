from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.script.types.function import BuiltInFunction
from ytdl_sub.script.types.resolvable import Argument
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.types.variable_dependency import VariableDependency


@dataclass(frozen=True)
class SyntaxTree(VariableDependency):
    ast: List[Argument]

    @property
    def iterable_arguments(self) -> List[Argument]:
        return self.ast

    def resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, VariableDependency],
    ) -> Resolvable:
        resolved: List[Resolvable] = []
        for token in self.ast:
            resolved.append(
                self._resolve_argument_type(
                    arg=token,
                    resolved_variables=resolved_variables,
                    custom_functions=custom_functions,
                )
            )

        # If only one resolvable resides in the AST, return as that
        if len(resolved) == 1:
            return resolved[0]

        # Otherwise, to concat multiple resolved outputs, we must concat as strings
        return String("".join([str(res) for res in resolved]))

    def partial_resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        unresolved_variables: Dict[Variable, Argument],
        custom_functions: Dict[str, VariableDependency],
    ) -> Argument | Resolvable:
        # Ensure this does not get returned as a SyntaxTree since nesting them is not supported.
        maybe_resolvable_values, _ = VariableDependency.try_partial_resolve(
            args=self.ast,
            resolved_variables=resolved_variables,
            unresolved_variables=unresolved_variables,
            custom_functions=custom_functions,
        )

        # Mimic the above resolve behavior
        if len(maybe_resolvable_values) > 1:
            return BuiltInFunction(name="concat", args=maybe_resolvable_values)

        return maybe_resolvable_values[0]

    @property
    def maybe_resolvable(self) -> Optional[Resolvable]:
        """
        Returns
        -------
        A resolvable if the AST contains a single type that is resolvable. None otherwise.
        """
        return None

    def maybe_resolvable_casted(self) -> "SyntaxTree":
        """
        Returns
        -------
        Optimized SyntaxTree if its deemed resolvable
        """
        if len(self.ast) == 1 and isinstance(self.ast[0], Resolvable):
            return ResolvedSyntaxTree(self.ast)
        return self


@dataclass(frozen=True)
class ResolvedSyntaxTree(SyntaxTree):
    """
    SyntaxTree with optimized helper functions if it's known to be resolved.
    """

    def resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, VariableDependency],
    ) -> Resolvable:
        return self.ast[0]

    @property
    def maybe_resolvable(self) -> Optional[Resolvable]:
        return self.ast[0]

    def partial_resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        unresolved_variables: Dict[Variable, Argument],
        custom_functions: Dict[str, VariableDependency],
    ) -> Argument | Resolvable:
        return self.ast[0]
