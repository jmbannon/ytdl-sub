from typing import List
from typing import Optional
from typing import Tuple
from unittest.mock import MagicMock
from unittest.mock import Mock

from ytdl_sub.cli.output_summary import output_summary


def test_output_summary_one_error():
    subscription_values: List[Tuple[str, int, int, int, int, Optional[Exception]]] = [
        ("long_name_but_lil_values", 0, 0, 0, 6, None),
        ("john_smith", 1, 0, 0, 52, None),
        ("david_gore", 0, 0, 0, 4, None),
        ("christopher_snoop", 50, 0, 3, 518, None),
        ("beyond funk", 0, 0, 0, 176, ValueError("lol")),
    ]

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

    _ = output_summary(subscriptions=mock_subscriptions)
    assert True  # Test used for manual inspection - too hard to test ansi color codes
