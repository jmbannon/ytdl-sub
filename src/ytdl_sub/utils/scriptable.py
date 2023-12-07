from abc import ABC
from typing import Set

from ytdl_sub.entries.script.variable_scripts import VARIABLE_SCRIPTS
from ytdl_sub.script.script import Script


class Scriptable(ABC):
    def __init__(self):
        self.script = Script(VARIABLE_SCRIPTS)
        self.unresolvable: Set[str] = set()

    def update_script(self) -> None:
        self.script.resolve(unresolvable=self.unresolvable, update=True)
