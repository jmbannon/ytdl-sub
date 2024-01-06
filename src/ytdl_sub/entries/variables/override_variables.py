from ytdl_sub.entries.script.function_scripts import CUSTOM_FUNCTION_SCRIPTS
from ytdl_sub.entries.script.variable_definitions import VARIABLE_SCRIPTS
from ytdl_sub.script.functions import Functions
from ytdl_sub.script.utils.name_validation import is_valid_name

# TODO: use this
SUBSCRIPTION_ARRAY = "subscription_array"


class SubscriptionVariables:
    @staticmethod
    def subscription_name() -> str:
        """
        Name of the subscription. For subscriptions types that use a prefix (``~``, ``+``),
        the prefix and all whitespace afterwards is stripped from the subscription name.
        """
        return "subscription_name"

    @staticmethod
    def subscription_value() -> str:
        """
        For subscriptions in the form of

        .. code-block:: yaml

           "Subscription Name": "https://..."

        ``subscription_value`` gets set to ``https://...``.
        """
        return "subscription_value"

    @staticmethod
    def subscription_indent_i(index: int) -> str:
        """
        For subscriptions in the form of

        .. code-block:: yaml

           Preset | = Indent Value 1:
             = Indent Value 2:
               "Subscription Name": "https://..."

        ``subscription_indent_1`` and ``subscription_indent_2`` get set to
        ``Indent Value 1`` and ``Indent Value 2``.
        """
        return f"subscription_indent_{index + 1}"

    @staticmethod
    def subscription_value_i(index: int) -> str:
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
        return f"subscription_value_{index + 1}"

    @staticmethod
    def subscription_map() -> str:
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
        return "subscription_map"


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
