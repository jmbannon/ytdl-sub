import copy
from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.validators.validators import DictValidator
from ytdl_sub.validators.validators import StringValidator
from ytdl_sub.validators.validators import Validator


class SubscriptionOutput(Validator, ABC):
    def __init__(self, name, value, presets: List[str]):
        super().__init__(name, value)
        self._presets = copy.deepcopy(presets)

    @abstractmethod
    def subscription_dicts(self) -> Dict[str, Dict]:
        """
        Returns
        -------
        Subscriptions in the form of ``{ subscription_name: preset_dict }``
        """


class SubscriptionPresetDictValidator(SubscriptionOutput, DictValidator):
    def subscription_dicts(self) -> Dict[str, Dict]:
        output_dict = copy.deepcopy(self._dict)
        parent_presets = output_dict.get("preset", [])

        # Preset can be a single string
        if isinstance(parent_presets, str):
            parent_presets = [parent_presets]

        output_dict["preset"] = parent_presets + self._presets
        return {self._leaf_name: output_dict}


class SubscriptionValueValidator(SubscriptionOutput, StringValidator):
    def __init__(self, name, value, presets: List[str], subscription_value: Optional[str]):
        super().__init__(name, value, presets)
        if subscription_value is None:
            raise self._validation_exception(
                f"Subscription {name} is a string, but the subscription value "
                f"is not set to an override variable"
            )

        self._subscription_value: str = subscription_value

    def subscription_dicts(self) -> Dict[str, Dict]:
        return {
            self._leaf_name: {
                "preset": self._presets,
                "overrides": {self._subscription_value: self.value},
            }
        }


class SubscriptionValidator(SubscriptionOutput):
    """
    Top-level subscription validator
    """

    def __init__(
        self, name, value, config: ConfigFile, presets: List[str], subscription_value: Optional[str]
    ):
        super().__init__(name, value, presets)
        self._children: List[SubscriptionOutput] = []

        for key, obj in value.items():
            obj_name = f"{name}.{key}" if name else key

            if isinstance(obj, str):
                if key in config.presets.keys:
                    raise self._validation_exception(
                        f"{key} conflicts with an existing preset name and cannot be "
                        f"used as a subscription name"
                    )

                self._children.append(
                    SubscriptionValueValidator(
                        name=obj_name,
                        value=obj,
                        presets=presets,
                        subscription_value=subscription_value,
                    )
                )
            elif isinstance(value, dict):
                if key in config.presets.keys:
                    self._children.append(
                        SubscriptionValidator(
                            name=obj_name,
                            value=obj,
                            config=config,
                            presets=presets + [key],
                            subscription_value=subscription_value,
                        )
                    )
                else:
                    self._children.append(
                        SubscriptionPresetDictValidator(name=obj_name, value=obj, presets=presets)
                    )

    def subscription_dicts(self) -> Dict[str, Dict]:
        subscription_dicts: Dict[str, Dict] = {}
        for child in self._children:
            subscription_dicts = dict(subscription_dicts, **child.subscription_dicts())

        return subscription_dicts
