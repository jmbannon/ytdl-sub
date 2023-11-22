from dataclasses import dataclass
from typing import Optional

from ytdl_sub.script.types.resolvable import ArgumentType


@dataclass(frozen=True)
class Variable(ArgumentType):
    name: str


@dataclass(frozen=True)
class FunctionArgument(Variable):
    """Arguments for custom functions, i.e. $0, $1, etc"""

    @classmethod
    def from_idx(cls, idx: int, custom_function_name: Optional[str]) -> "FunctionArgument":
        if custom_function_name:
            return FunctionArgument(name=f"${custom_function_name}___{idx}")
        return FunctionArgument(name=f"${idx}")
