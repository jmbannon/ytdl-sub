import copy
from abc import ABC
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set

from ytdl_sub.entries.script.function_scripts import CUSTOM_FUNCTION_SCRIPTS
from ytdl_sub.entries.script.variable_definitions import UNRESOLVED_VARIABLES
from ytdl_sub.entries.script.variable_definitions import VARIABLE_SCRIPTS
from ytdl_sub.entries.script.variable_types import Variable
from ytdl_sub.entries.variables.override_variables import REQUIRED_OVERRIDE_VARIABLE_DEFINITIONS
from ytdl_sub.script.script import Script
from ytdl_sub.script.utils.exceptions import RuntimeException
from ytdl_sub.utils.exceptions import StringFormattingException
from ytdl_sub.utils.script import ScriptUtils

BASE_SCRIPT: Script = Script(
    ScriptUtils.add_sanitized_variables(VARIABLE_SCRIPTS)
    | ScriptUtils.add_sanitized_variables(REQUIRED_OVERRIDE_VARIABLE_DEFINITIONS)
    | CUSTOM_FUNCTION_SCRIPTS
)


class Scriptable(ABC):
    """
    Shared class between Entry and Overrides to manage their underlying Script.
    """

    def __init__(self, initialize_base_script: bool = False):
        self._script: Optional[Script] = None
        self._unresolvable: Optional[Set[str]] = None

        if initialize_base_script:
            self.initialize_base_script()

    def initialize_base_script(self):
        """
        Initializes with base values
        """
        self._script = copy.deepcopy(BASE_SCRIPT)
        self._unresolvable = copy.deepcopy(UNRESOLVED_VARIABLES)

    @property
    def script(self) -> Script:
        """
        Initialized script
        """
        assert self._script is not None, "Not initialized"
        return self._script

    @property
    def unresolvable(self) -> Set[str]:
        """
        Initialized unresolvable variables
        """
        assert self._unresolvable is not None, "Not initialized"
        return self._unresolvable

    def update_script(self) -> None:
        """
        Updates any potential variables to a resolvable. This is done
        to avoid re-resolving the same variables over-and-over.
        """
        self.script.resolve(unresolvable=self.unresolvable, update=True)

    def add(self, values: Dict[str | Variable, Any]) -> None:
        """
        Add new values to the script
        """
        values_as_str: Dict[str, str] = {
            (var.variable_name if isinstance(var, Variable) else var): definition
            for var, definition in values.items()
        }

        self._unresolvable -= set(list(values_as_str.keys()))
        self.script.add(
            ScriptUtils.add_sanitized_variables(
                {
                    name: ScriptUtils.to_script(definition)
                    for name, definition in values_as_str.items()
                }
            ),
            unresolvable=self.unresolvable,
        )
        self.update_script()

        for name, definition in values_as_str.items():
            try:
                _ = self.script.get(variable_name=name)
            except RuntimeException as exc:
                raise StringFormattingException(
                    f"Tried to create the variable with name {name} and definition:\n"
                    f"{definition}\n"
                    f"But could not because it has variable dependencies that are not resolved yet"
                ) from exc
