import argparse
import sys
from typing import List
from typing import Tuple

from ytdl_sub.cli.download_args_parser import DownloadArgsParser
from ytdl_sub.cli.main_args_parser import parser
from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import Preset
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.file_handler import FileHandlerTransactionLog
from ytdl_sub.utils.logger import Logger

logger = Logger.get()


def _download_subscriptions_from_yaml_files(
    config: ConfigFile, args: argparse.Namespace
) -> List[Tuple[Subscription, FileHandlerTransactionLog]]:
    """
    Downloads all subscriptions from one or many subscription yaml files.

    Parameters
    ----------
    config
        Configuration file
    args
        Arguments from argparse

    Returns
    -------
    List of (subscription, transaction_log)
    """
    preset_paths: List[str] = args.subscription_paths
    presets: List[Preset] = []
    output: List[Tuple[Subscription, FileHandlerTransactionLog]] = []

    # Load all of the presets first to perform all validation before downloading
    for preset_path in preset_paths:
        presets += Preset.from_file_path(config=config, subscription_path=preset_path)

    for preset in presets:
        subscription = Subscription.from_preset(preset=preset, config=config)

        logger.info("Beginning subscription download for %s", subscription.name)
        transaction_log = subscription.download(dry_run=args.dry_run)

        output.append((subscription, transaction_log))

    return output


def _download_subscription_from_cli(
    config: ConfigFile, args: argparse.Namespace, extra_args: List[str]
) -> Tuple[Subscription, FileHandlerTransactionLog]:
    """
    Downloads a one-off subscription using the CLI

    Parameters
    ----------
    config
        Configuration file
    args
        Arguments from argparse
    extra_args
        Extra arguments from argparse that contain dynamic subscription options

    Returns
    -------
    Subscription and its download transaction log
    """
    dl_args_parser = DownloadArgsParser(
        extra_arguments=extra_args, config_options=config.config_options
    )
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

    return subscription, subscription.download(dry_run=args.dry_run)


def _main():
    """
    Entrypoint for ytdl-sub, without the error handling
    """
    # If no args are provided, print help and exit
    if len(sys.argv) < 2:
        parser.print_help()
        return

    args, extra_args = parser.parse_known_args()

    config: ConfigFile = ConfigFile.from_file_path(args.config).initialize()
    Logger.set_log_level(log_level_name=args.log_level)

    transaction_logs: List[Tuple[Subscription, FileHandlerTransactionLog]] = []
    if args.subparser == "sub":
        transaction_logs = _download_subscriptions_from_yaml_files(config=config, args=args)

    # One-off download
    if args.subparser == "dl":
        transaction_logs.append(
            _download_subscription_from_cli(config=config, args=args, extra_args=extra_args)
        )

    for subscription, transaction_log in transaction_logs:
        logger.info(
            "Downloads for %s:\n%s\n",
            subscription.name,
            transaction_log.to_output_message(subscription.output_directory),
        )

    # Ran successfully, so we can delete the debug file
    Logger.cleanup(delete_debug_file=True)


def main():
    """
    Entrypoint for ytdl-sub
    """
    try:
        _main()
    except ValidationException as validation_exception:
        logger.error(validation_exception)
        sys.exit(1)
    except Exception:  # pylint: disable=broad-except
        logger.exception("An uncaught error occurred:")
        logger.error(
            "Please upload the error log file '%s' and make a Github "
            "issue at https://github.com/jmbannon/ytdl-sub/issues with your config and "
            "command/subscription yaml file to reproduce. Thanks for trying ytdl-sub!",
            Logger.debug_log_filename(),
        )
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
