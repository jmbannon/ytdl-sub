from typing import Any
from typing import Optional
from typing import Set

from ytdl_subscribe.validators.base.object_validator import ObjectValidator
from ytdl_subscribe.validators.exceptions import ValidationException


class BaseSourceValidator(ObjectValidator):
    required_fields = {"download_strategy"}
    download_strategies: Set[str] = {}

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
        self.download_strategy: Optional[str] = None

    def validate(self) -> "BaseSourceValidator":
        super().validate()

        if self.value["download_strategy"] not in self.download_strategies:
            raise ValidationException(
                f"'download_strategy' must be one of the following: {', '.join(self.download_strategies)}"
            )

        return self
