import pytest
from unit.script.conftest import single_variable_output

from ytdl_sub.script.script import Script
from ytdl_sub.script.utils.exceptions import FunctionRuntimeException


class TestArrayFunctions:
    def test_array_extend(self):
        output = (
            Script(
                {
                    "array1": "{['a']}",
                    "array2": "{['b']}",
                    "array3": "{['c']}",
                    "output": "{%array_extend(array1, array2, array3)}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == ["a", "b", "c"]

    def test_array_at(self):
        output = single_variable_output("{%array_at(['a', 'b', 'c'], 1)}")
        assert output == "b"

    def test_array_at_default(self):
        output = single_variable_output("{%array_at(['a', 'b', 'c'], 30, 'd')}")
        assert output == "d"

    def test_array_at_error(self):
        with pytest.raises(FunctionRuntimeException):
            single_variable_output("{%array_at(['a', 'b', 'c'], 30)}")

    def test_array_flatten(self):
        output = single_variable_output("{%array_flatten(['a', ['b'], [['c']]])}")
        assert output == ["a", "b", "c"]

    def test_array_contains(self):
        output = single_variable_output("{%array_contains(['a', ['b'], [['c']]], [['c']])}")
        assert output is True

    def test_array_index(self):
        output = single_variable_output("{%array_index(['a', ['b'], [['c']]], [['c']])}")
        assert output == 2

    def test_array_slice(self):
        output = single_variable_output("{%array_slice(['a', ['b'], [['c']]], 1, -1)}")
        assert output == [["b"]]

    def test_array_reverse(self):
        output = single_variable_output("{%array_reverse(['a', 'b', 'c'])}")
        assert output == ["c", "b", "a"]

    def test_array_product(self):
        output = single_variable_output("{%array_product(['a', 'b', 'c'], ['arg'])}")
        assert output == [["a", "arg"], ["b", "arg"], ["c", "arg"]]

    def test_array_apply(self):
        output = single_variable_output("{%array_apply(['a', 'b', 'c'], %capitalize)}")
        assert output == ["A", "B", "C"]

    def test_array_reduce(self):
        output = single_variable_output("{%array_reduce([1, 2, 3, 4], %add)}")
        assert output == 10

    def test_array_reduce_complex(self):
        output = (
            Script(
                {
                    "%custom_get": """{
                        %if(
                            %bool(siblings_array),
                            %array_apply_fixed(
                                siblings_array,
                                %string($0),
                                %map_get
                            )
                            []
                        )
                    }""",
                    "siblings_array": """{
                        [
                            {'upload_date': '20200101'},
                            {'upload_date': '19940101'}
                        ]
                    }""",
                    "upload_date": "20230101",
                    "output": """{
                        %array_reduce(
                            %if_passthrough(
                                %custom_get('upload_date'),
                                [ upload_date ]
                            ),
                            %max
                        )
                    }""",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == "20200101"

    def test_array_enumerate(self):
        output = (
            Script(
                {
                    "%enumerate_output": "{[$0, $1]}",
                    "array1": "{['a', 'b', 'c']}",
                    "output": "{%array_enumerate(array1, %enumerate_output)}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == [[0, "a"], [1, "b"], [2, "c"]]

    def test_cast_array(self):
        output = (
            Script(
                {
                    "map_test": "{ {'key': [1, 2, 3]} }",
                    "output": "{ %array( %map_get(map_test, 'key') )}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == [1, 2, 3]

    def test_array_size(self):
        output = single_variable_output("{%array_size([1, 2, 3])}")
        assert output == 3

    def test_cast_array_errors_cannot_cast(self):
        with pytest.raises(
            FunctionRuntimeException, match="Tried and failed to cast Integer as an Array"
        ):
            single_variable_output("{%array(1)}")

    def test_array_overlay(self):
        output = single_variable_output("{%array_overlay([1, 2, 3], [4, 5])}")
        assert output == [4, 5, 3]

        output = single_variable_output("{%array_overlay([1, 2, 3], [4, 5, 6, 7, 8])}")
        assert output == [4, 5, 6, 7, 8]

        output = single_variable_output("{%array_overlay([1, 2, 3], [4, 5, 6, 7, 8], True)}")
        assert output == [1, 2, 3, 7, 8]

    def test_array_first(self):
        output = single_variable_output(
            "{%array_first(['', false, null, [], {}, 0, 'hi', 'no'], 'fallback')}"
        )
        assert output == "hi"

        output = single_variable_output("{%array_first(['', false, null, [], {}, 0], 'fallback')}")
        assert output == "fallback"

    def test_array_apply_fixed(self):
        output = (
            Script(
                {
                    "map_test": "{ {'key1': 7, 'key2': 8, 'key3': 9} }",
                    "output": """{
                        %array_apply_fixed( ['key1', 'key2', 'key3'], map_test, %map_get, True)
                    }""",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == [7, 8, 9]

        output = (
            Script(
                {
                    "output": "{%array_apply_fixed( ['key1', 'key2', 'key3'], '3', %contains)}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == [False, False, True]
