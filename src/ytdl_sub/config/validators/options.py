from abc import ABC
from typing import Dict
from typing import Set
from typing import TypeVar

from ytdl_sub.config.plugin.plugin_operation import PluginOperation
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import OverridesBooleanFormatterValidator
from ytdl_sub.validators.validators import Validator

# pylint: disable=unused-argument


class OptionsValidator(Validator, ABC):
    """
    Abstract class that validates options for preset sections (plugins, downloaders)
    """

    def validation_exception(
        self,
        error_message: str | Exception,
    ) -> ValidationException:
        """
        Parameters
        ----------
        error_message
            Error message to include in the validation exception

        Returns
        -------
        Validation exception that points to the location in the config. To be used to throw good
        validation exceptions at runtime from code outside this class.
        """
        return self._validation_exception(error_message=error_message)

    def modified_variables(self) -> Dict[PluginOperation, Set[str]]:
        """
        If the plugin modifies existing variables, define them here
        """
        return {}

    def added_variables(
        self,
        unresolved_variables: Set[str],
    ) -> Dict[PluginOperation, Set[str]]:
        """
        If the plugin adds source variables, list them here.
        """
        return {}


OptionsValidatorT = TypeVar("OptionsValidatorT", bound=OptionsValidator)


class OptionsDictValidator(StrictDictValidator, OptionsValidator, ABC):
    pass


class ToggleableOptionsDictValidator(OptionsDictValidator):
    _optional_keys = {"enable"}

    def __init__(self, name, value):
        assert (
            "enable" in self._optional_keys
        ), f"{self.__class__.__name__} does not have enable as an optional field"
        super().__init__(name, value)

        self._enable = self._validate_key(
            key="enable", validator=OverridesBooleanFormatterValidator, default="True"
        )

    @property
    def enable(self) -> OverridesBooleanFormatterValidator:
        """
        :expected type: Optional[OverridesFormatter]
        :description:
          Can typically be left undefined to always default to enable. For preset convenience,
          this field can be set using an override variable to easily toggle whether this plugin
          is enabled or not via Boolean.
        """
        return self._enable
