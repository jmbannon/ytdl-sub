from typing import List

from colorama import Fore

from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.logger import Logger

logger = Logger.get()


def _green(value: str) -> str:
    return Fore.GREEN + value + Fore.RESET


def _red(value: str) -> str:
    return Fore.RED + value + Fore.RESET


def _no_color(value: str) -> str:
    return Fore.RESET + value + Fore.RESET


def _str_int(value: int) -> str:
    if value > 0:
        return f"+{value}"
    return str(value)


def _color_int(value: int) -> str:
    str_int = _str_int(value)
    if value > 0:
        return _green(str_int)
    if value < 0:
        return _red(str_int)
    return _no_color(str_int)


def output_summary(subscriptions: List[Subscription]) -> None:
    """
    Parameters
    ----------
    subscriptions
        Processed subscriptions

    Returns
    -------
    Output summary to print
    """
    # many locals for proper output printing
    # pylint: disable=too-many-locals
    if len(subscriptions) == 0:
        logger.info("No subscriptions ran")
        return

    summary: List[str] = []

    # Initialize totals to 0
    total_subs: int = len(subscriptions)
    total_subs_str = f"Total: {total_subs}"
    total_added: int = sum(sub.num_entries_added for sub in subscriptions)
    total_modified: int = sum(sub.num_entries_modified for sub in subscriptions)
    total_removed: int = sum(sub.num_entries_removed for sub in subscriptions)
    total_entries: int = sum(sub.num_entries for sub in subscriptions)
    total_errors: int = sum(sub.exception is not None for sub in subscriptions)

    # Initialize widths to 0
    width_sub_name: int = max(len(sub.name) for sub in subscriptions) + 4  # aesthetics
    width_num_entries_added: int = len(_color_int(total_added))
    width_num_entries_modified: int = len(_color_int(total_modified))
    width_num_entries_removed: int = len(_color_int(total_removed))
    width_num_entries: int = len(str(total_entries)) + 4  # aesthetics

    # Build the summary
    for subscription in subscriptions:
        num_entries_added = _color_int(subscription.num_entries_added)
        num_entries_modified = _color_int(subscription.num_entries_modified)
        num_entries_removed = _color_int(subscription.num_entries_removed * -1)
        num_entries = str(subscription.num_entries)
        status = (
            _red(subscription.exception.__class__.__name__)
            if subscription.exception
            else _green("✔")
        )

        summary.append(
            f"{subscription.name:<{width_sub_name}} "
            f"{num_entries_added:>{width_num_entries_added}} "
            f"{num_entries_modified:>{width_num_entries_modified}} "
            f"{num_entries_removed:>{width_num_entries_removed}} "
            f"{num_entries:>{width_num_entries}} "
            f"{status}"
        )

    total_errors_str = (
        _green("Success") if total_errors == 0 else _red(f"Error{'s' if total_errors > 1 else ''}")
    )

    summary.append(
        f"{total_subs_str:<{width_sub_name}} "
        f"{_color_int(total_added):>{width_num_entries_added}} "
        f"{_color_int(total_modified):>{width_num_entries_modified}} "
        f"{_color_int(total_removed):>{width_num_entries_removed}} "
        f"{total_entries:>{width_num_entries}} "
        f"{total_errors_str}"
    )

    if total_errors > 0:
        summary.append("")
        summary.append(f"See `{Logger.error_log_filename()}` for details on errors.")
        summary.append("Consider making a GitHub issue including the uploaded log file.")

    # Hack to always show download summary, even if logs are set to quiet
    logger.warning("Download Summary:\n%s", "\n".join(summary))
