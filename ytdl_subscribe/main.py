import argparse
from ytdl_subscribe.parse import parse_subscriptions

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
parser.add_argument(
    "-s",
    "--subscriptions",
    metavar="SUB",
    nargs="+",
    help="specific subscriptions to download, downloads all if not provided",
)


if __name__ == "__main__":
    args = parser.parse_args()

    subscriptions = parse_subscriptions(args.config)
    if args.subscriptions:
        subscriptions = [s for s in subscriptions if s.name in args.subscriptions]

    for s in subscriptions:
        s.extract_info()
