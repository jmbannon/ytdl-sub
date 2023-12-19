from dataclasses import dataclass
from typing import Optional

from ytdl_sub.script.types.resolvable import NamedArgument


@dataclass(frozen=True)
class Variable(NamedArgument):
    pass


@dataclass(frozen=True)
class FunctionArgument(Variable):
    """Arguments for custom functions, i.e. $0, $1, etc"""

    index: int

    @classmethod
    def from_idx(cls, idx: int, custom_function_name: Optional[str]) -> "FunctionArgument":
        """
        Returns
        -------
        FunctionArgument whose variable name is the index, and optionally contains the custom
        function name its defined in as a prefix.
        """
        if custom_function_name:
            return FunctionArgument(name=f"${custom_function_name}___{idx}", index=idx)
        return FunctionArgument(name=f"${idx}", index=idx)
