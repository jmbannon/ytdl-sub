import argparse
import dataclasses
from enum import Enum
from typing import List
from typing import Optional

from ytdl_sub import __local_version__
from ytdl_sub.utils.logger import LoggerLevels


@dataclasses.dataclass
class MainArgument:
    short: str
    long: str
    is_positional: bool = False


class MainArguments:
    CONFIG = MainArgument(
        short="-c",
        long="--config",
    )
    DRY_RUN = MainArgument(
        short="-d",
        long="--dry-run",
        is_positional=True,
    )
    LOG_LEVEL = MainArgument(
        short="-l",
        long="--log-level",
        is_positional=True,
    )

    @classmethod
    def all(cls) -> List[MainArgument]:
        """
        Returns
        -------
        List of MainArgument classes
        """
        return [cls.CONFIG, cls.DRY_RUN, cls.LOG_LEVEL]

    @classmethod
    def all_arguments(cls) -> List[str]:
        """
        Returns
        -------
        List of all string args that can be used in the CLI
        """
        all_args = []
        for arg in cls.all():
            all_args.extend([arg.short, arg.long])
        return all_args

    @classmethod
    def get_argument_if_exists(cls, input_args: List[str]) -> Optional[str]:
        """
        Parameters
        ----------
        input_args
            List of arguments

        Returns
        -------
        True if a Main argument is in the input arguments. False otherwise.
        """
        for input_arg in input_args:
            for main_arg in cls.all_arguments():
                if input_arg == main_arg:
                    return input_arg
        return None


###################################################################################################
# GLOBAL PARSER
parser = argparse.ArgumentParser(
    description="ytdl-sub: Automate download and adding metadata with YoutubeDL"
)
parser.add_argument("--version", action="version", version="%(prog)s " + __local_version__)
parser.add_argument(
    MainArguments.CONFIG.short,
    MainArguments.CONFIG.long,
    metavar="CONFIGPATH",
    type=str,
    help="path to the config yaml, uses config.yaml if not provided",
    default="config.yaml",
)
parser.add_argument(
    MainArguments.DRY_RUN.short,
    MainArguments.DRY_RUN.long,
    action="store_true",
    help="preview what a download would output, "
    "does not perform any video downloads or writes to output directories",
)
parser.add_argument(
    MainArguments.LOG_LEVEL.short,
    MainArguments.LOG_LEVEL.long,
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
