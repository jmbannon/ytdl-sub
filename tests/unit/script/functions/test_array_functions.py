from ytdl_sub.script.script import Script


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
        output = (
            Script(
                {
                    "array1": "{['a', 'b', 'c']}",
                    "output": "{%array_at(array1, 1)}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == "b"

    def test_array_flatten(self):
        output = (
            Script(
                {
                    "array1": "{['a', ['b'], [['c']]]}",
                    "output": "{%array_flatten(array1)}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == ["a", "b", "c"]

    def test_array_reverse(self):
        output = (
            Script(
                {
                    "array1": "{['a', 'b', 'c']}",
                    "output": "{%array_reverse(array1)}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == ["c", "b", "a"]

    def test_array_apply(self):
        output = (
            Script(
                {
                    "array1": "{['a', 'b', 'c']}",
                    "output": "{%array_apply(array1, %capitalize)}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == ["A", "B", "C"]

    def test_array_enumerate(self):
        output = (
            Script(
                {
                    "%enumerate_output": "{[$0, $1]}",
                    "array1": "{['a', 'b', 'c']}",
                    "output": "{%array_apply(array1, %enumerate_output)}",
                }
            )
            .resolve(update=True)
            .get("output")
            .native
        )
        assert output == [[0, "a"], [1, "b"], [2, "c"]]
