import copy
from typing import Any
from typing import Dict
from typing import Type

from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.base.validators import StringValidator


class DownloadStrategyValidator(StrictDictValidator):
    pass


class SourceValidator(StrictDictValidator):
    # All media sources must define a download strategy
    required_keys = {"download_strategy"}

    # Extra fields will be strict-validated using other StictDictValidators
    allow_extra_keys = True

    download_strategy_validator_mapping: Dict[str, Type[DownloadStrategyValidator]] = {}

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
        self.download_strategy_name = self.validate_key(
            key="download_strategy",
            validator=StringValidator,
        ).value

        if self.download_strategy_name not in self.possible_download_strategies:
            raise self._validation_exception(
                f"download_strategy must be one of the following: {', '.join(self.possible_download_strategies)}"
            )

        # Remove all non-download strategy keys before passing the dict to the validator
        download_strategy_dict = copy.deepcopy(self.dict)
        for key_to_delete in self.allowed_keys:
            del download_strategy_dict[key_to_delete]

        download_strategy_class = self.download_strategy_validator_mapping[
            self.download_strategy_name
        ]
        self.download_strategy = download_strategy_class(
            name=self.name, value=download_strategy_dict
        )

    @property
    def possible_download_strategies(self):
        return sorted(list(self.download_strategy_validator_mapping.keys()))
