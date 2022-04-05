import argparse
import sys
from typing import List

###################################################################################################
# GLOBAL PARSER
from ytdl_subscribe.validators.config.config_validator import ConfigFileValidator
from ytdl_subscribe.validators.config.subscription_validator import (
    SubscriptionValidator,
)

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

    config: ConfigFileValidator = ConfigFileValidator.from_file_path(args.config)
    if args.subparser == "sub":
        subscription_paths: List[str] = args.subscription_paths
        subscriptions: List[SubscriptionValidator] = []

        for subscription_path in subscription_paths:
            subscriptions += SubscriptionValidator.from_file_path(
                config=config, subscription_path=subscription_path
            )

        for subscription in subscriptions:
            subscription.to_subscription().extract_info()

        print("hi")
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

    sys.exit(0)
