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
    summary: List[str] = []

    # Initialize totals to 0
    total_subs: int = 0
    total_added: int = 0
    total_modified: int = 0
    total_removed: int = 0
    total_entries: int = 0
    total_errors: int = 0

    # Initialize widths to 0
    width_sub_name: int = 0
    width_num_entries_added: int = 0
    width_num_entries_modified: int = 0
    width_num_entries_removed: int = 0
    width_num_entries: int = 0

    # Calculate min width needed
    for subscription in subscriptions:
        width_sub_name = max(width_sub_name, len(subscription.name))
        width_num_entries_added = max(
            width_num_entries_added, len(_color_int(subscription.num_entries_added))
        )
        width_num_entries_modified = max(
            width_num_entries_modified, len(_color_int(subscription.num_entries_modified))
        )
        width_num_entries_removed = max(
            width_num_entries_removed, len(_color_int(subscription.num_entries_removed * -1))
        )
        width_num_entries = max(width_num_entries, len(str(subscription.num_entries)))

    # Add spacing for aesthetics
    width_sub_name += 4
    width_num_entries += 4

    # Build the summary
    for subscription in subscriptions:
        num_entries_added = _color_int(subscription.num_entries_added)
        num_entries_modified = _color_int(subscription.num_entries_modified)
        num_entries_removed = _color_int(subscription.num_entries_removed * -1)
        num_entries = str(subscription.num_entries)
        status = _red("error") if subscription.exception else _green("success")

        summary.append(
            f"{subscription.name:<{width_sub_name}} "
            f"{num_entries_added:>{width_num_entries_added}} "
            f"{num_entries_modified:>{width_num_entries_modified}} "
            f"{num_entries_removed:>{width_num_entries_removed}} "
            f"{num_entries:>{width_num_entries}} "
            f"{status}"
        )

        # Add total
        total_subs += 1
        total_added += subscription.num_entries_added
        total_modified += subscription.num_entries_modified
        total_removed -= subscription.num_entries_removed
        total_entries += subscription.num_entries
        total_errors += int(subscription.exception is not None)

    total_subs_str = f"Total: {total_subs} Subscriptions"
    total_errors_str = (
        _green("All Successful")
        if total_errors == 0
        else _red(f"{total_errors} Error{'s' if total_errors > 1 else ''}")
    )

    summary.append("")  # new line
    summary.append(
        f"{total_subs_str:<{width_sub_name}} "
        f"{_color_int(total_added):>{width_num_entries_added}} "
        f"{_color_int(total_modified):>{width_num_entries_modified}} "
        f"{_color_int(total_removed):>{width_num_entries_removed}} "
        f"{str(total_entries):>{width_num_entries}} "
        f"{total_errors_str}"
    )

    if total_errors > 0:
        summary.append("")
        summary.append(f"See `{Logger.debug_log_filename()}` for details on errors.")
        summary.append("Consider making a GitHub issue including the uploaded log file.")

    # Hack to always show download summary, even if logs are set to quiet
    logger.warning("Download Summary:\n%s", "\n".join(summary))
