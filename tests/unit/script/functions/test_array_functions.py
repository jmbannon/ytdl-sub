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
