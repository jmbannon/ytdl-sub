import argparse
import sys
from random import randint
from typing import List

###################################################################################################
# GLOBAL PARSER
from ytdl_subscribe.cli.subscription_args_parser import SubscriptionArgsParser
from ytdl_subscribe.validators.config.config_file_validator import ConfigFileValidator
from ytdl_subscribe.validators.config.subscription_validator import SubscriptionValidator

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
# DOWNLOAD PARSER
download_parser = subparsers.add_parser("dl")

if __name__ == "__main__":
    args, extra_args = parser.parse_known_args()

    config: ConfigFileValidator = ConfigFileValidator.from_file_path(args.config)
    if args.subparser == "sub":
        subscription_paths: List[str] = args.subscription_paths
        subscriptions: List[SubscriptionValidator] = []

        for subscription_path in subscription_paths:
            subscriptions += SubscriptionValidator.from_file_path(
                config=config, subscription_path=subscription_path
            )

        for subscription in subscriptions:
            subscription.to_subscription().download()

        print("Subscription download complete!")

    # One-off download
    if args.subparser == "dl":
        subscription_name = f"cli-dl-{randint(0, 999)}"
        subscription_args_dict = SubscriptionArgsParser(
            extra_arguments=extra_args
        ).to_subscription_dict()
        SubscriptionValidator.from_dict(
            config=config,
            subscription_name=subscription_name,
            subscription_dict=subscription_args_dict,
        ).to_subscription().download()
        print("Download complete!")

    sys.exit(0)
