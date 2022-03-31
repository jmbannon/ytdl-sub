from typing import Any


class BaseValidator:
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value

    def validate(self) -> "BaseValidator":
        return self
