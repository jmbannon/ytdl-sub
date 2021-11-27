import argparse
from ytdl_subscribe.parse import (
    parse_subscriptions,
    parse_subscriptions_file,
    parse_presets,
)

parser = argparse.ArgumentParser(
    description="YoutubeDL-Subscribe: Download and organize your favorite media easily."
)
parser.add_argument(
    "-c",
    "--config",
    metavar="CONFIGPATH",
    type=str,
    help="path to the config yaml, uses subscriptions.yaml if not provided",
    default="subscriptions.yaml",
)
subparsers = parser.add_subparsers(dest="subparser")
subscription_parser = subparsers.add_parser("s")
subscription_parser.add_argument(
    "subscriptions",
    metavar="SUB",
    nargs="*",
    help="specific subscriptions to download, downloads all if not provided",
)
download_parser = subparsers.add_parser("dl")
download_parser.add_argument(
    "-p", "--preset", metavar="PRESET", help="which preset to apply"
)
download_parser.add_argument("-o", "--output", metavar="OUT", help="output path")
download_parser.add_argument(
    "-r",
    "--overrides",
    metavar="NAME:VALUE",
    nargs="+",
    help="variable overrides formmatted as name:value",
)

if __name__ == "__main__":
    args = parser.parse_args()

    print(args)

    # subscriptions = parse_subscriptions(args.config)

    yaml_dict = parse_subscriptions_file(args.config, set_config_variables=True)
    presets = parse_presets(yaml_dict)

    # Subscription download
    if args.subparser == "s":
        subscriptions = parse_subscriptions(
            yaml_dict, presets, subscriptions=args.subscriptions
        )
        for s in subscriptions:
            s.extract_info()

    # One-off download
    if args.subparser == "dl":
        preset = args.preset
        output_path = args.output_path
        overrides = args.overrides
