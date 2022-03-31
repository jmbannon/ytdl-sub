import argparse
from typing import List

from ytdl_subscribe.parse import parse_presets
from ytdl_subscribe.parse import parse_subscriptions
from ytdl_subscribe.parse import parse_subscriptions_file
from ytdl_subscribe.parse import read_config_file

###################################################################################################
# GLOBAL PARSER
from ytdl_subscribe.validators.config.config import Config

parser = argparse.ArgumentParser(
    description="YoutubeDL-Subscribe: Download and organize your favorite media hassle-free."
)
parser.add_argument(
    "-c",
    "--config",
    metavar="CONFIGPATH",
    type=str,
    help="path to the config yaml, uses config.yaml if not provided",
    default="config.yaml",
)
###################################################################################################
# SUBSCRIPTION PARSER
subparsers = parser.add_subparsers(dest="subparser")
subscription_parser = subparsers.add_parser("sub")
subscription_parser.add_argument(
    "subscription_paths",
    metavar="SUBPATH",
    nargs="*",
    help="path to subscription files, uses config.yaml if not provided",
    default="config.yaml",
)
###################################################################################################
# INTERACTIVE DOWNLOAD PARSER
download_parser = subparsers.add_parser("dl")
download_parser.add_argument(
    "url",
    help="url to the desired content to download, will prompt for further arguments needed",
)

if __name__ == "__main__":
    args = parser.parse_args()

    config: Config = Config.from_file_path(args.config)
    if args.subparser == "sub":
        subscription_paths: List[str] = args.subscription_paths

        # for subscription_path in subscription_paths:
        #
        #
        # subscriptions = parse_subscriptions(
        #     yaml_dict, presets, subscriptions=args.subscriptions
        # )
        # for s in subscriptions:
        #     s.extract_info()

    # One-off download
    if args.subparser == "dl":
        print("Interactive download is not supported yet. Stay tuned!")

    exit(0)
