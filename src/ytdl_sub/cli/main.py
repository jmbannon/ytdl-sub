import argparse
import gc
import sys
from typing import List
from typing import Tuple

from ytdl_sub.cli.download_args_parser import DownloadArgsParser
from ytdl_sub.cli.main_args_parser import parser
from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.file_handler import FileHandlerTransactionLog
from ytdl_sub.utils.file_lock import working_directory_lock
from ytdl_sub.utils.logger import Logger

logger = Logger.get()

# View is a command to run a simple dry-run on a URL using the `_view` preset.
# Use ytdl-sub dl arguments to use the preset
_VIEW_EXTRA_ARGS_FORMATTER = "--preset _view --overrides.url {}"


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
    subscription_paths: List[str] = args.subscription_paths
    subscriptions: List[Subscription] = []
    output: List[Tuple[Subscription, FileHandlerTransactionLog]] = []

    # Load all of the subscriptions first to perform all validation before downloading
    for path in subscription_paths:
        subscriptions += Subscription.from_file_path(config=config, subscription_path=path)

    for subscription in subscriptions:
        logger.info(
            "Beginning subscription %s for %s",
            ("dry run" if args.dry_run else "download"),
            subscription.name,
        )
        logger.debug("Subscription full yaml:\n%s", subscription.as_yaml())
        transaction_log = subscription.download(dry_run=args.dry_run)

        output.append((subscription, transaction_log))
        gc.collect()  # Garbage collect after each subscription download

    return output


def _download_subscription_from_cli(
    config: ConfigFile, dry_run: bool, extra_args: List[str]
) -> Tuple[Subscription, FileHandlerTransactionLog]:
    """
    Downloads a one-off subscription using the CLI

    Parameters
    ----------
    config
        Configuration file
    dry_run
        Whether this is a dry-run
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

    subscription = Subscription.from_dict(
        config=config, preset_name=subscription_name, preset_dict=subscription_args_dict
    )

    logger.info("Beginning CLI %s", ("dry run" if dry_run else "download"))
    return subscription, subscription.download(dry_run=dry_run)


def _view_url_from_cli(
    config: ConfigFile, url: str, split_chapters: bool
) -> Tuple[Subscription, FileHandlerTransactionLog]:
    """
    `ytdl-sub view` dry-runs a URL to print its source variables. Use the pre-built `_view` preset,
    inject the URL argument, and dry-run.
    """
    preset = "_view_split_chapters" if split_chapters else "_view"
    subscription = Subscription.from_dict(
        config=config,
        preset_name="ytdl-sub-view",
        preset_dict={"preset": preset, "overrides": {"url": url}},
    )

    logger.info(
        "Viewing source variables for URL '%s'%s",
        url,
        " with split chapters" if split_chapters else "",
    )
    return subscription, subscription.download(dry_run=True)


def main() -> List[Tuple[Subscription, FileHandlerTransactionLog]]:
    """
    Entrypoint for ytdl-sub, without the error handling
    """
    # If no args are provided, print help and exit
    if len(sys.argv) < 2:
        parser.print_help()
        return []

    args, extra_args = parser.parse_known_args()

    config: ConfigFile = ConfigFile.from_file_path(args.config).initialize()
    transaction_logs: List[Tuple[Subscription, FileHandlerTransactionLog]] = []

    with working_directory_lock(config=config):
        if args.subparser == "sub":
            transaction_logs = _download_subscriptions_from_yaml_files(config=config, args=args)

        # One-off download
        elif args.subparser == "dl":
            transaction_logs.append(
                _download_subscription_from_cli(
                    config=config, dry_run=args.dry_run, extra_args=extra_args
                )
            )
        elif args.subparser == "view":
            transaction_logs.append(
                _view_url_from_cli(config=config, url=args.url, split_chapters=args.split_chapters)
            )

    for subscription, transaction_log in transaction_logs:
        if transaction_log.is_empty:
            logger.info("No files changed for %s", subscription.name)
        else:
            logger.info(
                "Downloads for %s:\n%s\n",
                subscription.name,
                transaction_log.to_output_message(subscription.output_directory),
            )

    # Ran successfully, so we can delete the debug file
    Logger.cleanup(delete_debug_file=True)
    return transaction_logs
