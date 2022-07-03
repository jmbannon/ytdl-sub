from pathlib import Path
from typing import List

from ytdl_sub.utils.file_handler import FileHandlerTransactionLog

_TRANSACTION_LOG_SUMMARY_PATH = Path("tests/e2e/resources/transaction_log_summaries")


def assert_transaction_log_matches(
    output_directory: str,
    transaction_log: FileHandlerTransactionLog,
    transaction_log_summary_file_name: str,
):
    """
    Parameters
    ----------
    output_directory
        Output directory the files are saved to
    transaction_log
        Transaction log to check
    expected_transaction_log_summary
        Name if the transaction log summary to compare.
        Lives in tests/e2e/resources/transaction_log_summaries
    """

    with open(
        _TRANSACTION_LOG_SUMMARY_PATH / transaction_log_summary_file_name, "r", encoding="utf-8"
    ) as summary_file:
        expected_summary = summary_file.read()
    expected_summary = expected_summary.format(output_directory=output_directory)
    summary = transaction_log.to_output_message(output_directory=output_directory)

    # Ensure there are the same number of new lines
    summary_lines: List[str] = summary.split("\n")
    expected_summary_lines: List[str] = expected_summary.split("\n")

    assert len(summary_lines) == len(
        expected_summary_lines
    ), f"Summary number of lines differ: {len(summary_lines) != len(expected_summary_lines)}"

    for idx in range(len(summary_lines)):
        line = summary_lines[idx]
        expected_line = expected_summary_lines[idx]
        assert (
            summary_lines[idx] == expected_summary_lines[idx],
            f"Summary line {idx} differs: '{line}' != {expected_line}",
        )
