import logging
from typing import Any, Optional
from unittest.mock import patch

import pytest
from unit.script.conftest import single_variable_output



class TestPrintFunctions:
    @pytest.mark.parametrize(
        "function_str, expected_print, expected_output",
        [
            # print
            ("{%print('hi mom', True)}", 'hi mom', True),
            ("{%print('this is great', [1, 2, 3])}", 'this is great', [1, 2, 3]),
            ("{%print([1, 2], [3, 4])}", '[1, 2]', [3, 4]),
            # print_if_true
            ("{%print_if_true('hi mom', True)}", 'hi mom', True),
            ("{%print_if_true('hi mom', False)}", None, False),
            # print_if_false
            ("{%print_if_false('hi mom', True)}", None, True),
            ("{%print_if_false('hi mom', False)}", 'hi mom', False),
        ],
    )
    def test_print_functions(self, function_str: str, expected_print: Optional[str], expected_output: Any):
        with patch.object(logging.Logger, "info") as mock_logger:
            output = single_variable_output(function_str)
        assert output == expected_output

        if expected_print is not None:
            assert mock_logger.call_count == 1
            assert mock_logger.call_args.args[0] == expected_print
        else:
            assert mock_logger.call_count == 0

