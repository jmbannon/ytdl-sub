import os
from typing import List

from resources import RESOURCE_PATH

from ytdl_sub.utils.file_handler import FileHandlerTransactionLog

_TRANSACTION_LOG_SUMMARY_PATH = RESOURCE_PATH / "transaction_log_summaries"


def assert_transaction_log_matches(
    output_directory: str,
    transaction_log: FileHandlerTransactionLog,
    transaction_log_summary_file_name: str,
    regenerate_transaction_log: bool = True,
):
    """
    Parameters
    ----------
    output_directory
        Output directory the files are saved to
    transaction_log
        Transaction log to check
    transaction_log_summary_file_name
        Name if the transaction log summary to compare.
        Lives in tests/e2e/resources/transaction_log_summaries
    regenerate_transaction_log
        USE WITH CAUTION - MANUALLY INSPECT CHANGED FILES TO ENSURE THEY LOOK GOOD!
        Updates the file with the input transaction log. Should only be used to update
        tests after an expected change is made.
    """
    transaction_log_path = _TRANSACTION_LOG_SUMMARY_PATH / transaction_log_summary_file_name
    summary = transaction_log.to_output_message(output_directory=output_directory)

    # Write the expected summary file if regenerate is True
    if regenerate_transaction_log:
        os.makedirs(os.path.dirname(transaction_log_path), exist_ok=True)
        with open(transaction_log_path, "w", encoding="utf-8") as summary_file:
            summary_file.write(
                transaction_log.to_output_message(output_directory="{output_directory}")
            )

    # Read the expected summary file
    with open(transaction_log_path, "r", encoding="utf-8") as summary_file:
        expected_summary = summary_file.read().format(output_directory=output_directory)

    # Split, ensure there are the same number of new lines
    summary_lines: List[str] = summary.split("\n")
    expected_summary_lines: List[str] = expected_summary.split("\n")
    print(summary_lines)
    print(expected_summary_lines)
    assert len(summary_lines) == len(
        expected_summary_lines
    ), f"Summary number of lines differ: {len(summary_lines) != len(expected_summary_lines)}"

    # Ensure each line equals
    for idx in range(len(summary_lines)):
        line = summary_lines[idx]
        expected_line = expected_summary_lines[idx]
        assert line == expected_line, f"Summary line {idx} differs: '{line}' != '{expected_line}'"
