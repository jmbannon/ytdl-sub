from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union

from ytdl_sub.script.functions import Boolean
from ytdl_sub.script.functions import Float
from ytdl_sub.script.functions import Functions
from ytdl_sub.script.functions import Integer
from ytdl_sub.script.functions import String
from ytdl_sub.utils.exceptions import StringFormattingException


@dataclass(frozen=True)
class Variable:
    name: str


NumericType = Union[Integer, Float]
ArgumentType = Union[Integer, Float, String, Boolean, Variable, "Function"]


@dataclass(frozen=True)
class Function:
    name: str
    args: List[ArgumentType]

    def __post_init__(self):
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


@dataclass(frozen=True)
class LiteralString:
    value: str


@dataclass(frozen=True)
class SyntaxTree:
    ast: List[LiteralString | Variable | Function]

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
    def resolve(cls, parsed_overrides: Dict[str, "SyntaxTree"]) -> Dict[str, str]:
        raise NotImplemented()
