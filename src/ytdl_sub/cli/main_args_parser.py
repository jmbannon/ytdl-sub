import argparse
from enum import Enum
from typing import List

from ytdl_sub.utils.logger import LoggerLevels


class MainArgs(Enum):
    CONFIG = "--config"
    DRY_RUN = "--dry-run"
    LOG_LEVEL = "--log-level"

    @classmethod
    def all(cls) -> List[str]:
        """
        Returns
        -------
        List of all args used in main CLI
        """
        return list(map(lambda arg: arg.value, cls))


###################################################################################################
# GLOBAL PARSER
parser = argparse.ArgumentParser(
    description="ytdl-sub: Automate download and adding metadata with YoutubeDL"
)
parser.add_argument(
    "-c",
    MainArgs.CONFIG.value,
    metavar="CONFIGPATH",
    type=str,
    help="path to the config yaml, uses config.yaml if not provided",
    default="config.yaml",
)
parser.add_argument(
    MainArgs.DRY_RUN.value,
    action="store_true",
    help="does not perform any video downloads or writes to output directories",
)
parser.add_argument(
    MainArgs.LOG_LEVEL.value,
    metavar="|".join(LoggerLevels.names()),
    type=str,
    help="level of logs to print to console, defaults to info",
    default=LoggerLevels.INFO.name,
    choices=LoggerLevels.names(),
    dest="ytdl_sub_log_level",
)

subparsers = parser.add_subparsers(dest="subparser")
###################################################################################################
# SUBSCRIPTION PARSER
subscription_parser = subparsers.add_parser("sub")
subscription_parser.add_argument(
    "subscription_paths",
    metavar="SUBPATH",
    nargs="*",
    help="path to subscription files, uses subscriptions.yaml if not provided",
    default=["subscriptions.yaml"],
)
###################################################################################################
# DOWNLOAD PARSER
download_parser = subparsers.add_parser("dl")
###################################################################################################
# VIEW PARSER


class ViewArgs(Enum):
    SPLIT_CHAPTERS = "--split-chapters"

    @classmethod
    def all(cls) -> List[str]:
        """
        Returns
        -------
        List of all args used in main CLI
        """
        return list(map(lambda arg: arg.value, cls))


view_parser = subparsers.add_parser("view")
view_parser.add_argument(
    "-sc",
    ViewArgs.SPLIT_CHAPTERS.value,
    action="store_true",
    help="View source variables after splitting by chapters",
)
view_parser.add_argument("url", help="URL to view source variables for")
