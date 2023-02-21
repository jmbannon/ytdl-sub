import sys

from ytdl_sub import __local_version__
from ytdl_sub.cli.main_args_parser import parser
from ytdl_sub.utils.exceptions import ValidationException
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
    logger = Logger.get()
    try:
        _main()
    except ValidationException as validation_exception:
        logger.error(validation_exception)
        sys.exit(1)
    except Exception:  # pylint: disable=broad-except
        logger.exception("An uncaught error occurred:")
        logger.error(
            "Version %s\nPlease upload the error log file '%s' and make a Github "
            "issue at https://github.com/jmbannon/ytdl-sub/issues with your config and "
            "command/subscription yaml file to reproduce. Thanks for trying ytdl-sub!",
            __local_version__,
            Logger.debug_log_filename(),
        )
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
