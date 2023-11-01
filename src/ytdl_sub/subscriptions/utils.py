SUBSCRIPTION_NAME = "subscription_name"
SUBSCRIPTION_VALUE = "subscription_value"

# Key used in configs, should delete at some point
SUBSCRIPTION_VALUE_CONFIG_KEY = "subscription_value"


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


def subscription_list_variable_name(index: int) -> str:
    """
    Parameters
    ----------
    index
        0th-based index

    Returns
    -------
    subscription_value_i, where i is 1-based index
    """
    return f"subscription_value_{index + 1}"
