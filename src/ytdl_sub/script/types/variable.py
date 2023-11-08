from dataclasses import dataclass

from ytdl_sub.script.types.resolvable import ArgumentType


@dataclass(frozen=True)
class Variable(ArgumentType):
    name: str
