SUBSCRIPTION_NAME = "subscription_name"
SUBSCRIPTION_VALUE = "subscription_value"


class OverrideVariables:
    @classmethod
    def subscription_name(cls) -> str:
        """
        Name of the subscription
        """
        return SUBSCRIPTION_NAME

    @classmethod
    def subscription_value(cls) -> str:
        """
        For subscriptions in the form of

        .. code-block:: yaml

           "Subscription Name": "https://..."

        ``subscription_value`` gets set to ``https://...``.
        """
        return SUBSCRIPTION_VALUE

    @classmethod
    def subscription_indent_i(cls, index: int) -> str:
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

    @classmethod
    def subscription_value_i(cls, index: int) -> str:
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
