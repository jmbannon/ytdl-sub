from typing import Any


class Validator:
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value

    def validate(self) -> "Validator":
        return self
