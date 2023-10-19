from typing import List
from typing import Tuple

from colorama import Fore

from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.file_handler import FileHandlerTransactionLog
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


def output_summary(transaction_logs: List[Tuple[Subscription, FileHandlerTransactionLog]]) -> str:
    """
    Parameters
    ----------
    transaction_logs
        Transaction logs from downloaded subscriptions

    Returns
    -------
    Output summary to print
    """
    summary: List[str] = []

    # Initialize widths to 0
    width_sub_name: int = 0
    width_num_entries_added: int = 0
    width_num_entries_modified: int = 0
    width_num_entries_removed: int = 0
    width_num_entries: int = 0

    # Calculate min width needed
    for subscription, _ in transaction_logs:
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
    for subscription, _ in transaction_logs:
        num_entries_added = _color_int(subscription.num_entries_added)
        num_entries_modified = _color_int(subscription.num_entries_modified)
        num_entries_removed = _color_int(subscription.num_entries_removed * -1)
        num_entries = str(subscription.num_entries)
        status = _green("success")

        summary.append(
            f"{subscription.name:<{width_sub_name}} "
            f"{num_entries_added:>{width_num_entries_added}} "
            f"{num_entries_modified:>{width_num_entries_modified}} "
            f"{num_entries_removed:>{width_num_entries_removed}} "
            f"{num_entries:>{width_num_entries}} "
            f"{status}"
        )

    # Hack to always show download summary, even if logs are set to quiet
    logger.warning("Download Summary:\n%s", "\n".join(summary))
