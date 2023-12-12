from dataclasses import dataclass
from typing import Any
from typing import Dict

from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.utils.exceptions import ScriptVariableNotResolved


@dataclass(frozen=True)
class ScriptOutput:
    output: Dict[str, Resolvable]

    def as_resolvable(self) -> Dict[str, Resolvable]:
        return self.output

    def as_native(self) -> Dict[str, Any]:
        return {name: out.native for name, out in self.output.items()}

    def get(self, name: str) -> Resolvable:
        if name not in self.output:
            raise ScriptVariableNotResolved(
                f"Tried to access resolved variable {name}, but it has not resolved"
            )
        return self.output[name]

    def get_native(self, name: str) -> Any:
        return self.get(name).native

    def get_str(self, name: str) -> str:
        return str(self.get(name))

    def get_int(self, name: str) -> int:
        out = self.get_native(name)
        assert isinstance(out, int)
        return out
