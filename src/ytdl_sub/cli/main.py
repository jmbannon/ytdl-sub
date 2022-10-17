import argparse
import errno
import fcntl
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import List
from typing import Tuple

from ytdl_sub.cli.download_args_parser import DownloadArgsParser
from ytdl_sub.cli.main_args_parser import parser
from ytdl_sub.config.config_file import ConfigFile
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
    subscription_paths: List[str] = args.subscription_paths
    subscriptions: List[Subscription] = []
    output: List[Tuple[Subscription, FileHandlerTransactionLog]] = []

    # Load all of the subscriptions first to perform all validation before downloading
    for path in subscription_paths:
        subscriptions += Subscription.from_file_path(config=config, subscription_path=path)

    for subscription in subscriptions:
        logger.info("Beginning subscription download for %s", subscription.name)
        logger.debug("Subscription full yaml:\n%s", subscription.as_yaml())
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

    subscription = Subscription.from_dict(
        config=config, preset_name=subscription_name, preset_dict=subscription_args_dict
    )

    return subscription, subscription.download(dry_run=args.dry_run)


@contextmanager
def _working_directory_lock(config: ConfigFile):
    """
    Create and try to lock the file /tmp/working_directory_name

    Raises
    ------
    ValidationException
        Lock is acquired from another process running ytdl-sub in the same working directory
    OSError
        Other lock error occurred
    """
    working_directory_path = Path(os.getcwd()) / config.config_options.working_directory
    lock_file_path = Path(tempfile.gettempdir()) / str(working_directory_path).replace("/", "_")

    lock_file = open(lock_file_path, "w", encoding="utf-8")

    try:
        fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        if exc.errno in (errno.EACCES, errno.EAGAIN):
            raise ValidationException(
                "Cannot run two instances of ytdl-sub "
                "with the same working directory at the same time"
            ) from exc
        lock_file.close()
        raise exc

    try:
        yield
    finally:
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()


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

    with _working_directory_lock(config=config):
        if args.subparser == "sub":
            transaction_logs = _download_subscriptions_from_yaml_files(config=config, args=args)

        # One-off download
        if args.subparser == "dl":
            transaction_logs.append(
                _download_subscription_from_cli(config=config, args=args, extra_args=extra_args)
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
