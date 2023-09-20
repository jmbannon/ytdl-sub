from dataclasses import dataclass


@dataclass(frozen=True)
class Variable:
    name: str
