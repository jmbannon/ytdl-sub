import copy
import dataclasses
from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List
from typing import Optional
from typing import final

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.overrides import Overrides
from ytdl_sub.entries.variables.override_variables import SubscriptionVariables
from ytdl_sub.utils.script import ScriptUtils
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.validators import DictValidator
from ytdl_sub.validators.validators import LiteralDictValidator
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
            SubscriptionVariables.subscription_indent_i(i).variable_name: self._indent_overrides[i]
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


class NamedSubscriptionValidator(SubscriptionOutput, ABC):
    def __init__(
        self, name, value, subscription_name: str, presets: List[str], indent_overrides: List[str]
    ):
        super().__init__(name=name, value=value, presets=presets, indent_overrides=indent_overrides)
        self.subscription_name = subscription_name


class SubscriptionPresetDictValidator(NamedSubscriptionValidator, DictValidator):
    def __init__(
        self, name, value, subscription_name: str, presets: List[str], indent_overrides: List[str]
    ):
        super().__init__(
            name=name,
            value=value,
            subscription_name=subscription_name,
            presets=presets,
            indent_overrides=indent_overrides,
        )

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
        )
        return {self.subscription_name: output_dict}


class SubscriptionLeafValidator(NamedSubscriptionValidator, ABC):
    def __init__(
        self,
        name,
        value,
        subscription_name: str,
        config: ConfigFile,
        presets: List[str],
        indent_overrides: List[str],
    ):
        super().__init__(
            name=name,
            value=value,
            subscription_name=subscription_name,
            presets=presets,
            indent_overrides=indent_overrides,
        )

        if self.subscription_name in config.presets.keys:
            raise self._validation_exception(
                f"{self.subscription_name} conflicts with an existing preset name and cannot be "
                f"used as a subscription name"
            )

        self._overrides_to_add: Dict[str, str] = {}

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
        subscription_name: str,
        config: ConfigFile,
        presets: List[str],
        indent_overrides: List[str],
    ):
        super().__init__(
            name=name,
            value=value,
            subscription_name=subscription_name,
            config=config,
            presets=presets,
            indent_overrides=indent_overrides,
        )
        # subscription_value
        self._overrides_to_add[SubscriptionVariables.subscription_value().variable_name] = (
            self.value
        )

        # subscription_value_0
        self._overrides_to_add[
            SubscriptionVariables.subscription_value_i(index=0).variable_name
        ] = self.value

        # And the array variable
        self._overrides_to_add[SubscriptionVariables.subscription_array().variable_name] = (
            ScriptUtils.to_script([self.value])
        )


class SubscriptionListValuesValidator(SubscriptionLeafValidator, StringListValidator):
    def __init__(
        self,
        name,
        value,
        subscription_name: str,
        config: ConfigFile,
        presets: List[str],
        indent_overrides: List[str],
    ):
        super().__init__(
            name=name,
            value=value,
            subscription_name=subscription_name,
            config=config,
            presets=presets,
            indent_overrides=indent_overrides,
        )

        # Add indexed variables
        for idx, list_value in enumerate(self.list):
            # Write the first list value into subscription_value as well
            if idx == 0:
                self._overrides_to_add[SubscriptionVariables.subscription_value().variable_name] = (
                    list_value.value
                )

            self._overrides_to_add[
                SubscriptionVariables.subscription_value_i(index=idx).variable_name
            ] = list_value.value

        # And the array variable
        self._overrides_to_add[SubscriptionVariables.subscription_array().variable_name] = (
            ScriptUtils.to_script([list_value.value for list_value in self.list])
        )


class SubscriptionWithOverridesValidator(SubscriptionLeafValidator, DictFormatterValidator):
    def __init__(
        self,
        name,
        value,
        subscription_name: str,
        config: ConfigFile,
        presets: List[str],
        indent_overrides: List[str],
    ):
        super().__init__(
            name=name,
            value=value,
            subscription_name=subscription_name,
            config=config,
            presets=presets,
            indent_overrides=indent_overrides,
        )

        self._overrides_to_add = dict(self.dict_with_format_strings, **self._overrides_to_add)


class SubscriptionMapValidator(SubscriptionLeafValidator, LiteralDictValidator):
    def __init__(
        self,
        name,
        value,
        subscription_name: str,
        config: ConfigFile,
        presets: List[str],
        indent_overrides: List[str],
    ):
        super().__init__(
            name=name,
            value=value,
            subscription_name=subscription_name,
            config=config,
            presets=presets,
            indent_overrides=indent_overrides,
        )
        self._overrides_to_add[SubscriptionVariables.subscription_map().variable_name] = (
            ScriptUtils.to_script(self.dict, sort_keys=False)
        )


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
                        subscription_name=key,
                        config=config,
                        presets=presets,
                        indent_overrides=indent_overrides,
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
                        subscription_name=key,
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
                            subscription_name=key[1:].lstrip(),
                            config=config,
                            presets=presets,
                            indent_overrides=indent_overrides,
                        )
                    )
                # Subscription defined as
                # "\Sub Name":
                #   custom_key: "value"
                elif key.startswith("+"):
                    self._children.append(
                        SubscriptionMapValidator(
                            name=obj_name,
                            value=obj,
                            subscription_name=key[1:].lstrip(),
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
                        )
                    )
                else:
                    self._children.append(
                        SubscriptionPresetDictValidator(
                            name=obj_name,
                            value=obj,
                            subscription_name=key,
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
