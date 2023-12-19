from dataclasses import dataclass
from typing import Any
from typing import Dict

from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.utils.exceptions import ScriptVariableNotResolved


@dataclass(frozen=True)
class ScriptOutput:
    output: Dict[str, Resolvable]

    def as_native(self) -> Dict[str, Any]:
        """
        Returns
        -------
        The script output as native python types
        """
        return {name: out.native for name, out in self.output.items()}

    def get(self, name: str) -> Resolvable:
        """
        Returns
        -------
        The script output's variable as a resolvable type

        Raises
        ------
        ScriptVariableNotResolved
            The variable name requested did not resolve
        """
        if name not in self.output:
            raise ScriptVariableNotResolved(
                f"Tried to access resolved variable {name}, but it has not resolved"
            )
        return self.output[name]

    def get_native(self, name: str) -> Any:
        """
        Returns
        -------
        The script output's variable as native python type
        """
        return self.get(name).native

    def get_str(self, name: str) -> str:
        """
        Returns
        -------
        The script output's variable as a string
        """
        return str(self.get(name))
