import sys

from ytdl_sub.cli.parsers.main import parser
from ytdl_sub.utils.logger import Logger


def _main() -> int:
    # Set log level before any other ytdl-sub files are imported. That way, when loggers
    # get initialized, they will see the set log level
    args, _ = parser.parse_known_args()
    Logger.set_log_level(log_level_name=args.ytdl_sub_log_level)

    # pylint: disable=import-outside-toplevel
    import ytdl_sub.cli.entrypoint

    # pylint: enable=import-outside-toplevel

    subs = ytdl_sub.cli.entrypoint.main()
    if any(sub.exception for sub in subs):
        return 1  # Return error-code if any exceptions occurred
    return 0


def main():
    """
    Entrypoint for ytdl-sub
    """
    try:
        return_code = _main()
        Logger.cleanup(has_error=return_code != 0)
        sys.exit(return_code)
    except Exception as exc:  # pylint: disable=broad-except
        Logger.log_exception(exception=exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
