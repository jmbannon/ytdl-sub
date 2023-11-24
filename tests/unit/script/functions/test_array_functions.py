from ytdl_sub.script.script import Script


class TestArrayFunctions:
    def test_array_extend(self):
        assert Script(
            {
                "array1": "{['a', 3.14]}",
                "array2": "{['b', 8.8]}",
                "array3": "{['c', 3.17]}",
                "array_extended_output": "{%array_extend(array1, array2, array3)}",
            }
        ).resolve(update=True).get("array_extended_output").native == [
            "a",
            3.14,
            "b",
            8.8,
            "c",
            3.17,
        ]
