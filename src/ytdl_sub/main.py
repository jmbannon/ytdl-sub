import argparse
import sys
import traceback
from typing import List

from ytdl_sub.cli.download_args_parser import DownloadArgsParser
from ytdl_sub.cli.main_args_parser import parser
from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.subscription import SubscriptionValidator
from ytdl_sub.logging import YtdlSubLogger
from ytdl_sub.utils.exceptions import ValidationException

DEBUGGER_MODE = True

logger = YtdlSubLogger.logger()


def _download_subscriptions_from_yaml_files(config: ConfigFile, args: argparse.Namespace) -> None:
    """
    Downloads all subscriptions from one or many subscription yaml files.

    :param config: Configuration file
    :param args: Arguments from argparse
    """
    subscription_paths: List[str] = args.subscription_paths
    subscriptions: List[SubscriptionValidator] = []

    for subscription_path in subscription_paths:
        subscriptions += SubscriptionValidator.from_file_path(
            config=config, subscription_path=subscription_path
        )

    for subscription in subscriptions:
        logger.info("Beginning subscription download for %s", subscription.name)
        subscription.to_subscription().download()


def _download_subscription_from_cli(config: ConfigFile, extra_args: List[str]) -> None:
    """
    Downloads a one-off subscription using the CLI

    :param config: Configuration file
    :param extra_args: Extra arguments from argparse that contain dynamic subscription options
    """
    dl_args_parser = DownloadArgsParser(extra_arguments=extra_args)
    subscription_args_dict = dl_args_parser.to_subscription_dict()

    subscription_name = f"cli-dl-{dl_args_parser.get_args_hash()}"
    SubscriptionValidator.from_dict(
        config=config,
        subscription_name=subscription_name,
        subscription_dict=subscription_args_dict,
    ).to_subscription().download()


def main():
    """Entrypoint for ytdl-subscribe"""
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
        if DEBUGGER_MODE:
            raise
        logger.error(validation_exception)
        sys.exit(1)
    except Exception as exc:  # pylint: disable=broad-except
        if DEBUGGER_MODE:
            raise
        print(traceback.format_exc())
        print(
            "A fatal error occurred. Please copy and paste the stacktrace above and make a Github "
            "issue at https://github.com/jmbannon/ytdl-subscribe/issues with your config and "
            "command/subscription yaml file to reproduce. Thanks for trying ytdl-subscribe!"
        )
        sys.exit(1)

    sys.exit(0)
