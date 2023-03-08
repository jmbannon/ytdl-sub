import sys

from ytdl_sub.cli.main_args_parser import parser
from ytdl_sub.utils.logger import Logger


def _main():
    # Set log level before any other ytdl-sub files are imported. That way, when loggers
    # get initialized, they will see the set log level
    args, _ = parser.parse_known_args()
    Logger.set_log_level(log_level_name=args.ytdl_sub_log_level)

    # pylint: disable=import-outside-toplevel
    import ytdl_sub.cli.main

    # pylint: enable=import-outside-toplevel

    ytdl_sub.cli.main.main()


def main():
    """
    Entrypoint for ytdl-sub
    """
    try:
        _main()
        Logger.cleanup()  # Ran successfully, so we can delete the debug file
    except Exception as exc:  # pylint: disable=broad-except
        Logger.log_exit_exception(exception=exc)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
