from resources import REGENERATE_FIXTURES


def test_regenerate_fixtures_is_false() -> None:
    """Make sure this is always set to False when committing"""
    assert not REGENERATE_FIXTURES