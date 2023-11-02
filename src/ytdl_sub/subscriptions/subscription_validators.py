import copy
import dataclasses
from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List
from typing import Optional
from typing import final

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.subscriptions.utils import SUBSCRIPTION_NAME
from ytdl_sub.subscriptions.utils import SUBSCRIPTION_VALUE
from ytdl_sub.subscriptions.utils import subscription_indent_variable_name
from ytdl_sub.subscriptions.utils import subscription_list_variable_name
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.validators import DictValidator
from ytdl_sub.validators.validators import StringListValidator
from ytdl_sub.validators.validators import StringValidator
from ytdl_sub.validators.validators import Validator


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
    def subscription_dicts(self, global_presets_to_apply: List[str]) -> Dict[str, Dict]:
        """
        Parameters

        Returns
        -------
        Subscriptions in the form of ``{ subscription_name: preset_dict }``
        """

    @property
    def subscription_name(self) -> str:
        """
        Returns
        -------
        The name of the subscription
        """
        return self._leaf_name


class SubscriptionPresetDictValidator(SubscriptionOutput, DictValidator):
    def __init__(self, name, value, presets: List[str], indent_overrides: List[str]):
        super().__init__(name=name, value=value, presets=presets, indent_overrides=indent_overrides)

        _ = self._validate_key_if_present(key="preset", validator=StringListValidator, default=[])
        _ = self._validate_key_if_present(key="overrides", validator=Overrides, default={})

    def subscription_dicts(self, global_presets_to_apply: List[str]) -> Dict[str, Dict]:
        output_dict = copy.deepcopy(self._dict)
        parent_presets = output_dict.get("preset", [])

        # Preset can be a single string
        if isinstance(parent_presets, str):
            parent_presets = [parent_presets]

        output_dict["preset"] = parent_presets + self._presets + global_presets_to_apply
        output_dict["overrides"] = dict(
            output_dict.get("overrides", {}),
            **self._indent_overrides_dict(),
            **{SUBSCRIPTION_NAME: self.subscription_name},
        )
        return {self.subscription_name: output_dict}


class SubscriptionLeafValidator(SubscriptionOutput, ABC):
    def __init__(
        self,
        name,
        value,
        config: ConfigFile,
        presets: List[str],
        indent_overrides: List[str],
    ):
        super().__init__(name=name, value=value, presets=presets, indent_overrides=indent_overrides)

        if self.subscription_name in config.presets.keys:
            raise self._validation_exception(
                f"{self.subscription_name} conflicts with an existing preset name and cannot be "
                f"used as a subscription name"
            )

        self._overrides_to_add: Dict[str, str] = {SUBSCRIPTION_NAME: self.subscription_name}

    @final
    def subscription_dicts(self, global_presets_to_apply: List[str]) -> Dict[str, Dict]:
        return {
            self.subscription_name: {
                "preset": self._presets + global_presets_to_apply,
                "overrides": dict(
                    self._indent_overrides_dict(),
                    **self._overrides_to_add,
                ),
            }
        }


class SubscriptionValueValidator(SubscriptionLeafValidator, StringValidator):
    def __init__(
        self,
        name,
        value,
        config: ConfigFile,
        presets: List[str],
        indent_overrides: List[str],
        subscription_value: Optional[str],
    ):
        super().__init__(
            name=name,
            value=value,
            config=config,
            presets=presets,
            indent_overrides=indent_overrides,
        )

        # TODO: Eventually delete in favor of {subscription_value}
        if subscription_value:
            self._overrides_to_add[subscription_value] = self.value
        self._overrides_to_add[SUBSCRIPTION_VALUE] = self.value


class SubscriptionListValuesValidator(SubscriptionLeafValidator, StringListValidator):
    def __init__(
        self,
        name,
        value,
        config: ConfigFile,
        presets: List[str],
        indent_overrides: List[str],
    ):
        super().__init__(
            name=name,
            value=value,
            config=config,
            presets=presets,
            indent_overrides=indent_overrides,
        )

        for idx, list_value in enumerate(self.list):
            # Write the first list value into subscription_value as well
            if idx == 0:
                self._overrides_to_add[SUBSCRIPTION_VALUE] = list_value.value

            self._overrides_to_add[subscription_list_variable_name(index=idx)] = list_value.value


class SubscriptionWithOverridesValidator(SubscriptionLeafValidator, DictFormatterValidator):
    def __init__(
        self,
        name,
        value,
        config: ConfigFile,
        presets: List[str],
        indent_overrides: List[str],
    ):
        super().__init__(
            name=name,
            value=value,
            config=config,
            presets=presets,
            indent_overrides=indent_overrides,
        )

        self._overrides_to_add = dict(self.dict_with_format_strings, **self._overrides_to_add)

    @property
    def subscription_name(self) -> str:
        """
        Returns
        -------
        Name of the subscription
        """
        # drop the ~ in "~Subscription Name":
        return super().subscription_name[1:]


class SubscriptionValidator(SubscriptionOutput):
    """
    Top-level subscription validator
    """

    @dataclasses.dataclass
    class PresetIndentKey:
        presets: List[str] = dataclasses.field(default_factory=list)
        indent_overrides: List[str] = dataclasses.field(default_factory=list)

    def _preset_indent_key(self, key: str, config: ConfigFile) -> Optional[PresetIndentKey]:
        presets: List[str] = []
        indent_overrides: List[str] = []

        stripped_split_keys = [sub_key.strip() for sub_key in key.split("|")]
        for sub_key in stripped_split_keys:
            if sub_key.startswith("="):
                indent_overrides.append(sub_key[1:].strip())
            elif sub_key in config.presets.keys:
                presets.append(sub_key)
            else:
                if presets or indent_overrides:
                    raise self._validation_exception(
                        f"'{sub_key.strip()}' in '{key.strip()}' is not a preset name. "
                        f"To use as a subscription indent value, define it as '= {sub_key.strip()}'"
                    )

        if not presets and not indent_overrides:
            return None

        return SubscriptionValidator.PresetIndentKey(
            presets=presets, indent_overrides=indent_overrides
        )

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

            # Subscription defined as
            # "Sub Name": "value"
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
            # Subscription defined as
            # "Sub Name":
            #   - "value1"
            #   - "value2"
            elif isinstance(obj, list):
                self._children.append(
                    SubscriptionListValuesValidator(
                        name=obj_name,
                        value=obj,
                        config=config,
                        presets=presets,
                        indent_overrides=indent_overrides,
                    )
                )
            elif isinstance(obj, dict):
                # Subscription defined as
                # "~Sub Name":
                #   override_1: "abc"
                #   override_2: "123"
                if key.startswith("~"):
                    self._children.append(
                        SubscriptionWithOverridesValidator(
                            name=obj_name,
                            value=obj,
                            config=config,
                            presets=presets,
                            indent_overrides=indent_overrides,
                        )
                    )
                elif (
                    preset_indent_key := self._preset_indent_key(key=key, config=config)
                ) is not None:
                    self._children.append(
                        SubscriptionValidator(
                            name=obj_name,
                            value=obj,
                            config=config,
                            presets=presets + preset_indent_key.presets,
                            indent_overrides=indent_overrides + preset_indent_key.indent_overrides,
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
            else:
                raise self._validation_exception(
                    "Subscription value should either be a string, list, or object"
                )

    def subscription_dicts(self, global_presets_to_apply: List[str]) -> Dict[str, Dict]:
        subscription_dicts: Dict[str, Dict] = {}
        for child in self._children:
            subscription_dicts = dict(
                subscription_dicts,
                **child.subscription_dicts(global_presets_to_apply=global_presets_to_apply),
            )

        return subscription_dicts
