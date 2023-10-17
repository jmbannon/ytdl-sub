import copy
from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.validators.validators import DictValidator
from ytdl_sub.validators.validators import StringListValidator
from ytdl_sub.validators.validators import StringValidator
from ytdl_sub.validators.validators import Validator


def subscription_indent_variable_name(index: int) -> str:
    """
    Parameters
    ----------
    index
        0th-based index

    Returns
    -------
    subscription_index_i, where i is 1-based index
    """
    return f"subscription_indent_{index + 1}"


def subscription_value_variable_name() -> str:
    """
    Returns
    -------
    The override variable name containing the subscription value if present
    """
    return "subscription_value"


def maybe_indent_override_values(value: str) -> List[str]:
    """
    Returns
    -------
    Value if it is an overide [Value]. None otherwise.
    """
    if value.startswith("="):
        # Drop the =, split on |, and strip each indent_value (both left + right)
        return [indent_value.strip() for indent_value in value[1:].split("|")]
    return []


class SubscriptionOutput(Validator, ABC):
    def __init__(self, name, value, presets: List[str], indent_overrides: List[str]):
        super().__init__(name, value)
        self._presets = copy.deepcopy(presets)
        self._indent_overrides = copy.deepcopy(indent_overrides)

    def _indent_overrides_dict(self) -> Dict[str, str]:
        """
        Returns
        -------
        indent overrides to merge with the preset dict's overrides
        """
        return {
            subscription_indent_variable_name(i): self._indent_overrides[i]
            for i in range(len(self._indent_overrides))
        }

    @abstractmethod
    def subscription_dicts(self) -> Dict[str, Dict]:
        """
        Returns
        -------
        Subscriptions in the form of ``{ subscription_name: preset_dict }``
        """


class SubscriptionPresetDictValidator(SubscriptionOutput, DictValidator):
    def __init__(self, name, value, presets: List[str], indent_overrides: List[str]):
        super().__init__(name=name, value=value, presets=presets, indent_overrides=indent_overrides)

        _ = self._validate_key_if_present(key="preset", validator=StringListValidator, default=[])
        _ = self._validate_key_if_present(key="overrides", validator=Overrides, default={})

    def subscription_dicts(self) -> Dict[str, Dict]:
        output_dict = copy.deepcopy(self._dict)
        parent_presets = output_dict.get("preset", [])

        # Preset can be a single string
        if isinstance(parent_presets, str):
            parent_presets = [parent_presets]

        output_dict["preset"] = parent_presets + self._presets
        output_dict["overrides"] = dict(
            output_dict.get("overrides", {}), **self._indent_overrides_dict()
        )
        return {self._leaf_name: output_dict}


class SubscriptionValueValidator(SubscriptionOutput, StringValidator):
    def __init__(
        self,
        name,
        value,
        config: ConfigFile,
        presets: List[str],
        indent_overrides: List[str],
        subscription_value: Optional[str],
    ):
        super().__init__(name=name, value=value, presets=presets, indent_overrides=indent_overrides)

        if self._leaf_name in config.presets.keys:
            raise self._validation_exception(
                f"{self._leaf_name} conflicts with an existing preset name and cannot be "
                f"used as a subscription name"
            )
        self._subscription_value: Optional[str] = subscription_value

    def subscription_dicts(self) -> Dict[str, Dict]:
        subscription_value_dict: Dict[str, str] = {"subscription_value": self.value}
        # TODO: Eventually delete in favor of {subscription_value}
        if self._subscription_value:
            subscription_value_dict[self._subscription_value] = self.value

        return {
            self._leaf_name: {
                "preset": self._presets,
                "overrides": dict(
                    subscription_value_dict,
                    **self._indent_overrides_dict(),
                ),
            }
        }


class SubscriptionValidator(SubscriptionOutput):
    """
    Top-level subscription validator
    """

    def __init__(
        self,
        name,
        value,
        config: ConfigFile,
        presets: List[str],
        indent_overrides: List[str],
        subscription_value: Optional[str],
    ):
        super().__init__(name=name, value=value, presets=presets, indent_overrides=indent_overrides)
        self._children: List[SubscriptionOutput] = []

        for key, obj in value.items():
            obj_name = f"{name}.{key}" if name else key

            if isinstance(obj, str):
                self._children.append(
                    SubscriptionValueValidator(
                        name=obj_name,
                        value=obj,
                        config=config,
                        presets=presets,
                        indent_overrides=indent_overrides,
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
                            indent_overrides=indent_overrides,
                            subscription_value=subscription_value,
                        )
                    )
                elif override_values := maybe_indent_override_values(key):
                    self._children.append(
                        SubscriptionValidator(
                            name=obj_name,
                            value=obj,
                            config=config,
                            presets=presets,
                            indent_overrides=indent_overrides + override_values,
                            subscription_value=subscription_value,
                        )
                    )
                else:
                    self._children.append(
                        SubscriptionPresetDictValidator(
                            name=obj_name,
                            value=obj,
                            presets=presets,
                            indent_overrides=indent_overrides,
                        )
                    )

    def subscription_dicts(self) -> Dict[str, Dict]:
        subscription_dicts: Dict[str, Dict] = {}
        for child in self._children:
            subscription_dicts = dict(subscription_dicts, **child.subscription_dicts())

        return subscription_dicts
