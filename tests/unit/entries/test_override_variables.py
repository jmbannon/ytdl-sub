import pytest

from ytdl_sub.entries.variables.override_variables import OverrideVariables


class TestOverrideVariables:
    @pytest.mark.parametrize(
        "override_variable_name",
        [
            "subscription_value",
            "subscription_name",
            "subscription_map",
            "subscription_array",
            "subscription_value_532",
            "subscription_indent_0",
            "subscription_indent_1",
        ],
    )
    def test_override_variables_contains(self, override_variable_name: str):
        assert OverrideVariables.is_override_variable_name(override_variable_name)

    @pytest.mark.parametrize(
        "override_variable_name",
        [
            "subscription_value_var",
            "subscription_name_var",
            "subscription_map_var",
            "subscription_array_var",
            "subscription_value_532_var",
            "subscription_indent_0_var",
            "subscription_indent_1_var",
        ],
    )
    def test_override_variables_does_not_contains(self, override_variable_name: str):
        assert not OverrideVariables.is_override_variable_name(override_variable_name)
