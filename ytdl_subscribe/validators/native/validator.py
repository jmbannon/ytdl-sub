from typing import Any


class Validator:
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value

    def validate(self) -> "Validator":
        return self
