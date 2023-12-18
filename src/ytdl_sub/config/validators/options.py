from abc import ABC
from typing import Dict
from typing import Set
from typing import TypeVar

from ytdl_sub.config.plugin.plugin_operation import PluginOperation
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.validators import Validator

# pylint: disable=no-self-use
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
        resolved_variables: Set[str],
        unresolved_variables: Set[str],
        plugin_op: PluginOperation,
    ) -> Dict[PluginOperation, Set[str]]:
        """
        If the plugin adds source variables, list them here.
        """
        return {}


TOptionsValidator = TypeVar("TOptionsValidator", bound=OptionsValidator)


class OptionsDictValidator(StrictDictValidator, OptionsValidator, ABC):
    pass
