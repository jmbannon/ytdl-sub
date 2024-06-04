from typing import Dict
from typing import Set

from ytdl_sub.entries.script.function_scripts import CUSTOM_FUNCTION_SCRIPTS
from ytdl_sub.entries.script.variable_definitions import VARIABLE_SCRIPTS
from ytdl_sub.entries.script.variable_types import ArrayVariable
from ytdl_sub.entries.script.variable_types import BooleanVariable
from ytdl_sub.entries.script.variable_types import MapVariable
from ytdl_sub.entries.script.variable_types import StringVariable
from ytdl_sub.entries.script.variable_types import Variable
from ytdl_sub.script.functions import Functions
from ytdl_sub.script.utils.name_validation import is_valid_name

# TODO: use this
SUBSCRIPTION_ARRAY = "subscription_array"


class SubscriptionVariables:
    @staticmethod
    def subscription_name() -> StringVariable:
        """
        Name of the subscription. For subscriptions types that use a prefix (``~``, ``+``),
        the prefix and all whitespace afterwards is stripped from the subscription name.
        """
        return StringVariable(variable_name="subscription_name", definition="{ %string('') }")

    @staticmethod
    def subscription_value() -> StringVariable:
        """
        For subscriptions in the form of

        .. code-block:: yaml

           "Subscription Name": "https://..."

        ``subscription_value`` gets set to ``https://...``.
        """
        return StringVariable(variable_name="subscription_value", definition="{ %string('') }")

    @staticmethod
    def subscription_array() -> ArrayVariable:
        """
        For subscriptions in the form of

        .. code-block:: yaml

           "Subscription Name":
             - "https://url1.com/..."
             - "https://url2.com/..."

        Store all values into an array named ``subscription_array``.
        """
        return ArrayVariable(variable_name="subscription_array", definition="{ [] }")

    @staticmethod
    def subscription_indent_i(index: int) -> StringVariable:
        """
        For subscriptions in the form of

        .. code-block:: yaml

           Preset | = Indent Value 1:
             = Indent Value 2:
               "Subscription Name": "https://..."

        ``subscription_indent_1`` and ``subscription_indent_2`` get set to
        ``Indent Value 1`` and ``Indent Value 2``.
        """
        return StringVariable(
            variable_name=f"subscription_indent_{index + 1}", definition="{ %string('') }"
        )

    @staticmethod
    def subscription_value_i(index: int) -> StringVariable:
        """
        For subscriptions in the form of

        .. code-block:: yaml

           "Subscription Name":
             - "https://url1.com/..."
             - "https://url2.com/..."

        ``subscription_value_1`` and ``subscription_value_2`` get set to ``https://url1.com/...``
        and ``https://url2.com/...``. Note that ``subscription_value_1`` also gets set to
        ``subscription_value``.
        """
        return StringVariable(
            variable_name=f"subscription_value_{index + 1}", definition="{ %string('') }"
        )

    @staticmethod
    def subscription_map() -> MapVariable:
        """
        For subscriptions in the form of

        .. code-block:: yaml

           + Subscription Name:
             Music Videos:
               - "https://url1.com/..."
             Concerts:
               - "https://url2.com/..."

        Stores all the contents under the subscription name into the override variable
        ``subscription_map`` as a Map value. The above example is stored as:

        .. code-block:: python

           {
             "Music Videos": [
               "https://url1.com/..."
             ],
             "Concerts: [
               "https://url2.com/..."
             ]
           }
        """
        return MapVariable(variable_name="subscription_map", definition="{ {} }")

    @staticmethod
    def subscription_has_download_archive() -> BooleanVariable:
        """
        Returns True if the subscription has any entries recorded in a download archive. False
        otherwise.
        """
        return BooleanVariable(
            variable_name="subscription_has_download_archive", definition="{ %bool(True) }"
        )


class OverrideHelpers:
    @classmethod
    def is_entry_variable_name(cls, name: str) -> bool:
        """
        Returns
        -------
        True if the name is an entry variable name. False otherwise.
        """
        return name in VARIABLE_SCRIPTS

    @classmethod
    def is_function_name(cls, name: str) -> bool:
        """
        Returns
        -------
        True if the name is a function name (either built-in or script). False otherwise.
        """
        if name.startswith("%"):
            return name in CUSTOM_FUNCTION_SCRIPTS or Functions.is_built_in(name[1:])
        return False

    @classmethod
    def is_valid_name(cls, name: str) -> bool:
        """
        Returns
        -------
        True if the override name itself is valid. False otherwise.
        """
        if name.startswith("%"):
            return is_valid_name(name=name[1:])

        return is_valid_name(name=name)


REQUIRED_OVERRIDE_VARIABLES: Set[Variable] = {
    SubscriptionVariables.subscription_name(),
    SubscriptionVariables.subscription_has_download_archive(),
}

REQUIRED_OVERRIDE_VARIABLE_DEFINITIONS: Dict[str, str] = {
    var.variable_name: var.definition for var in REQUIRED_OVERRIDE_VARIABLES
}

REQUIRED_OVERRIDE_VARIABLE_NAMES: Set[str] = {
    var.variable_name for var in REQUIRED_OVERRIDE_VARIABLES
}
