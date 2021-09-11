import argparse
from ytdl_subscribe.parse import parse_subscriptions

parser = argparse.ArgumentParser(
    description="YoutubeDL-Subscribe: Download and organize your favorite media easily."
)
parser.add_argument(
    "--config",
    type=str,
    help="Path to the config yaml. Will look for subscriptions.yaml in the current directory if not provided",
    default="subscriptions.yaml",
)


if __name__ == "__main__":
    args = parser.parse_args()

    # execute only if run as a script
    subscriptions = parse_subscriptions(args.config)
    for s in subscriptions:
        s.extract_info()
    print("hey")
