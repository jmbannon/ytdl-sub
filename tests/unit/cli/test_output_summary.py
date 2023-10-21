from typing import List
from typing import Optional
from typing import Tuple
from unittest.mock import MagicMock
from unittest.mock import Mock

from ytdl_sub.cli.output_summary import output_summary


def _to_mock_subscriptions(
    subscription_values: List[Tuple[str, int, int, int, int, Optional[Exception]]]
) -> List[MagicMock]:
    mock_subscriptions: List[MagicMock] = []
    for values in subscription_values:
        sub = Mock()
        sub.name = values[0]
        sub.num_entries_added = values[1]
        sub.num_entries_modified = values[2]
        sub.num_entries_removed = values[3]
        sub.num_entries = values[4]
        sub.exception = values[5]

        mock_subscriptions.append(sub)

    return mock_subscriptions


def test_output_summary_no_errors():
    mock_subscriptions = _to_mock_subscriptions(
        [
            ("long_name_but_lil_values", 0, 0, 0, 6, None),
            ("john_smith", 1, 0, 0, 52, None),
            ("david_gore", 0, 0, 0, 4, None),
            ("christopher_snoop", 50, 0, 3, 518, None),
            ("beyond funk", 352, 0, 0, 2342, None),
        ]
    )

    output_summary(subscriptions=mock_subscriptions)


def test_output_summary_one_error():
    mock_subscriptions = _to_mock_subscriptions(
        [
            ("long_name_but_lil_values", 0, 0, 0, 6, None),
            ("john_smith", 1, 0, 0, 52, None),
            ("david_gore", 0, 0, 0, 4, None),
            ("christopher_snoop", 50, 0, 3, 518, None),
            ("beyond funk", 0, 0, 0, 176, ValueError("lol")),
        ]
    )

    output_summary(subscriptions=mock_subscriptions)


def test_output_summary_multiple_errors():
    mock_subscriptions = _to_mock_subscriptions(
        [
            ("long_name_but_lil_values", 0, 0, 0, 6, None),
            ("john_smith", 1, 0, 0, 52, None),
            ("david_gore", 0, 0, 0, 4, PermissionError("ack")),
            ("christopher_snoop", 50, 0, 3, 518, None),
            ("beyond funk", 0, 0, 0, 176, ValueError("lol")),
        ]
    )

    output_summary(subscriptions=mock_subscriptions)
