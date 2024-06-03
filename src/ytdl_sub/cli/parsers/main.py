import argparse
import dataclasses
from typing import List

from ytdl_sub import __local_version__
from ytdl_sub.utils.logger import LoggerLevels

DEFAULT_CONFIG_FILE_NAME: str = "config.yaml"


@dataclasses.dataclass
class CLIArgument:
    short: str
    long: str
    is_positional: bool = False


class MainArguments:
    CONFIG = CLIArgument(
        short="-c",
        long="--config",
    )
    DRY_RUN = CLIArgument(
        short="-d",
        long="--dry-run",
        is_positional=True,
    )
    LOG_LEVEL = CLIArgument(
        short="-l",
        long="--log-level",
        is_positional=True,
    )
    TRANSACTION_LOG = CLIArgument(
        short="-t",
        long="--transaction-log",
        is_positional=True,
    )
    SUPPRESS_TRANSACTION_LOG = CLIArgument(
        short="-st",
        long="--suppress-transaction-log",
        is_positional=True,
    )
    MATCH = CLIArgument(
        short="-m",
        long="--match",
    )

    @classmethod
    def all(cls) -> List[CLIArgument]:
        """
        Returns
        -------
        List of MainArgument classes
        """
        return [
            cls.CONFIG,
            cls.DRY_RUN,
            cls.LOG_LEVEL,
            cls.TRANSACTION_LOG,
            cls.SUPPRESS_TRANSACTION_LOG,
            cls.MATCH,
        ]

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


###################################################################################################
# SHARED OPTIONS
def _add_shared_arguments(arg_parser: argparse.ArgumentParser, suppress_defaults: bool) -> None:
    """
    Add shared arguments to sub parsers. Needed to be able to specify args after positional args.
    i.e. support both ``ytdl-sub --dry-run sub`` and ``ytdl-sub sub --dry-run``

    Parameters
    ----------
    arg_parser
        The parser to add shared args to
    suppress_defaults
        bool. Suppress sub parser defaults so they do not override the defaults in the parent parser
    """
    arg_parser.add_argument(
        MainArguments.CONFIG.short,
        MainArguments.CONFIG.long,
        metavar="CONFIGPATH",
        type=str,
        help=f"path to the config yaml, uses {DEFAULT_CONFIG_FILE_NAME} if not provided",
        default=argparse.SUPPRESS if suppress_defaults else None,  # Default is set downstream
    )
    arg_parser.add_argument(
        MainArguments.DRY_RUN.short,
        MainArguments.DRY_RUN.long,
        action="store_true",
        help="preview what a download would output, "
        "does not perform any video downloads or writes to output directories",
        default=argparse.SUPPRESS if suppress_defaults else False,
    )
    arg_parser.add_argument(
        MainArguments.LOG_LEVEL.short,
        MainArguments.LOG_LEVEL.long,
        metavar="|".join(LoggerLevels.names()),
        type=str,
        help="level of logs to print to console, defaults to info",
        default=argparse.SUPPRESS if suppress_defaults else LoggerLevels.INFO.name,
        choices=LoggerLevels.names(),
        dest="ytdl_sub_log_level",
    )
    arg_parser.add_argument(
        MainArguments.TRANSACTION_LOG.short,
        MainArguments.TRANSACTION_LOG.long,
        metavar="TRANSACTIONPATH",
        type=str,
        help="path to store the transaction log output of all files added, modified, deleted",
        default=argparse.SUPPRESS if suppress_defaults else "",
    )
    arg_parser.add_argument(
        MainArguments.SUPPRESS_TRANSACTION_LOG.short,
        MainArguments.SUPPRESS_TRANSACTION_LOG.long,
        action="store_true",
        help="do not output transaction logs to console or file",
        default=argparse.SUPPRESS if suppress_defaults else False,
    )
    arg_parser.add_argument(
        MainArguments.MATCH.short,
        MainArguments.MATCH.long,
        dest="match",
        nargs="+",
        action="extend",
        type=str,
        help="match subscription names to one or more substrings, and only run those subscriptions",
        default=argparse.SUPPRESS if suppress_defaults else [],
    )


###################################################################################################
# GLOBAL PARSER
parser = argparse.ArgumentParser(
    description="ytdl-sub: Automate download and adding metadata with YoutubeDL",
)
parser.add_argument("-v", "--version", action="version", version="%(prog)s " + __local_version__)
_add_shared_arguments(parser, suppress_defaults=False)

subparsers = parser.add_subparsers(dest="subparser")


###################################################################################################
# SUBSCRIPTION PARSER
class SubArguments:
    UPDATE_WITH_INFO_JSON = CLIArgument(
        short="-u",
        long="--update-with-info-json",
    )
    OVERRIDE = CLIArgument(
        short="-o",
        long="--dl-override",
    )


subscription_parser = subparsers.add_parser("sub")
_add_shared_arguments(subscription_parser, suppress_defaults=True)
subscription_parser.add_argument(
    "subscription_paths",
    metavar="SUBPATH",
    nargs="*",
    help="path to subscription files, uses subscriptions.yaml if not provided",
    default=["subscriptions.yaml"],
)
subscription_parser.add_argument(
    SubArguments.UPDATE_WITH_INFO_JSON.short,
    SubArguments.UPDATE_WITH_INFO_JSON.long,
    action="store_true",
    help="update all subscriptions with the current config using info.json files",
    default=False,
)
subscription_parser.add_argument(
    SubArguments.OVERRIDE.short,
    SubArguments.OVERRIDE.long,
    type=str,
    help="override all subscription config values using `dl` syntax, "
    "i.e. --dl-override='--ytdl_options.max_downloads 3'",
)

###################################################################################################
# DOWNLOAD PARSER
download_parser = subparsers.add_parser("dl")
###################################################################################################
# VIEW PARSER


class ViewArguments:
    SPLIT_CHAPTERS = CLIArgument(
        short="-sc",
        long="--split-chapters",
    )


view_parser = subparsers.add_parser("view")
_add_shared_arguments(view_parser, suppress_defaults=True)
view_parser.add_argument(
    ViewArguments.SPLIT_CHAPTERS.short,
    ViewArguments.SPLIT_CHAPTERS.long,
    action="store_true",
    help="View source variables after splitting by chapters",
)
view_parser.add_argument("url", help="URL to view source variables for")
