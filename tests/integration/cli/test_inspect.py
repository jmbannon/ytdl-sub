from pathlib import Path

import pytest
import yaml
from conftest import mock_run_from_cli
from unit.config.test_subscription_resolution import compare_resolved_yaml

from ytdl_sub.config.validators.variable_validation import ResolutionLevel


class TestInspect:
    @pytest.mark.parametrize("config_provided", [True, False])
    @pytest.mark.parametrize(
        "inspect_level", ["0", "original", "1", "fill", "2", "resolve", "3", "internal"]
    )
    def test_inspect_command(
        self,
        capsys,
        default_config_path: str,
        tv_show_subscriptions_path: Path,
        output_directory: str,
        config_provided: bool,
        inspect_level: str,
    ):
        # Shares same test fixture as `test_subscription_resolution.py`
        args = f"--config {default_config_path} " if config_provided else ""
        args += f"inspect {tv_show_subscriptions_path} --match 'NOVA PBS' "
        args += f"--level {inspect_level}"

        subscriptions = mock_run_from_cli(args=args)
        assert len(subscriptions) == 0

        out = yaml.safe_load(capsys.readouterr().out)
        compare_resolved_yaml(
            out=out,
            output_directory=output_directory,
            subscription_name="NOVA PBS",
            preset_type="tv_show",
            resolution_level=ResolutionLevel.level_number(resolution_arg=inspect_level),
        )
