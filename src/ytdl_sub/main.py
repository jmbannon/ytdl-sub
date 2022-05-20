import argparse
import sys
from typing import List

from ytdl_sub.cli.download_args_parser import DownloadArgsParser
from ytdl_sub.cli.main_args_parser import parser
from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import Preset
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.logger import Logger

logger = Logger.get()


def _download_subscriptions_from_yaml_files(config: ConfigFile, args: argparse.Namespace) -> None:
    """
    Downloads all subscriptions from one or many subscription yaml files.

    :param config: Configuration file
    :param args: Arguments from argparse
    """
    preset_paths: List[str] = args.subscription_paths
    presets: List[Preset] = []

    for preset_path in preset_paths:
        presets += Preset.from_file_path(config=config, subscription_path=preset_path)

    for preset in presets:
        subscription = Subscription.from_preset(preset=preset, config=config)

        logger.info("Beginning subscription download for %s", subscription.name)
        subscription.download()


def _download_subscription_from_cli(config: ConfigFile, extra_args: List[str]) -> None:
    """
    Downloads a one-off subscription using the CLI

    :param config: Configuration file
    :param extra_args: Extra arguments from argparse that contain dynamic subscription options
    """
    dl_args_parser = DownloadArgsParser(extra_arguments=extra_args)
    subscription_args_dict = dl_args_parser.to_subscription_dict()

    subscription_name = f"cli-dl-{dl_args_parser.get_args_hash()}"
    subscription_preset = Preset.from_dict(
        config=config,
        preset_name=subscription_name,
        preset_dict=subscription_args_dict,
    )

    subscription = Subscription.from_preset(
        preset=subscription_preset,
        config=config,
    )

    subscription.download()


def main():
    """
    Entrypoint for ytdl-subscribe
    """
    # If no args are provided, print help and exit
    if len(sys.argv) < 2:
        parser.print_help()
        return

    args, extra_args = parser.parse_known_args()

    config: ConfigFile = ConfigFile.from_file_path(args.config)
    if args.subparser == "sub":
        _download_subscriptions_from_yaml_files(config=config, args=args)
        logger.info("Subscription download complete!")

    # One-off download
    if args.subparser == "dl":
        _download_subscription_from_cli(config=config, extra_args=extra_args)
        logger.info("Download complete!")


if __name__ == "__main__":
    try:
        main()
    except ValidationException as validation_exception:
        logger.error(validation_exception)
        sys.exit(1)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception(
            "A fatal error occurred. Please copy and paste the stacktrace above and make a Github "
            "issue at https://github.com/jmbannon/ytdl-subscribe/issues with your config and "
            "command/subscription yaml file to reproduce. Thanks for trying ytdl-subscribe!"
        )
        sys.exit(1)

    sys.exit(0)
