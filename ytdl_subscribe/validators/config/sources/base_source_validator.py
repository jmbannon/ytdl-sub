from typing import Any
from typing import Optional
from typing import Set

from ytdl_subscribe.validators.base.dict_validator import DictValidator
from ytdl_subscribe.validators.base.string_validator import StringValidator
from ytdl_subscribe.validators.exceptions import ValidationException


class BaseSourceValidator(DictValidator):
    # All media sources must define a download strategy
    required_fields = {"download_strategy"}
    download_strategies: Set[str] = {}

    def _validate_and_get_download_strategy(self) -> str:
        download_strategy = self.validate_dict_value(
            dict_value_name="download_strategy",
            validator=StringValidator,
        )

        if download_strategy.value not in self.download_strategies:
            raise self._validation_exception(
                f"download_strategy must be one of the following: {', '.join(self.download_strategies)}"
            )

        return download_strategy.value

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
        self.download_strategy = self._validate_and_get_download_strategy()
