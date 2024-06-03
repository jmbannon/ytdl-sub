from unit.script.conftest import single_variable_output


class TestCustomFunctions:
    def test_is_playlist_ordered_by_newest_true(self):
        assert (
            single_variable_output(
                "{%is_playlist_ordered_by_newest('https://www.youtube.com/playlist?list=PL5BC0FC26BECA5A35')}"
            )
            is True
        )

    def test_is_playlist_ordered_by_newest_false(self):
        assert (
            single_variable_output(
                "{%is_playlist_ordered_by_newest('https://www.youtube.com/playlist?list=PL2KvlCGf4yFftX466OnFS8wvuSosBfUgm')}"
            )
            is False
        )

    def test_is_playlist_ordered_by_newest_defaults_false(self):
        assert single_variable_output("{%is_playlist_ordered_by_newest('aaaaaa')}") is False
