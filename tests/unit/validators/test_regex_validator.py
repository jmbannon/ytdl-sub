import pytest

from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.validators.regex_validator import RegexListValidator
from ytdl_sub.validators.regex_validator import RegexValidator


@pytest.mark.parametrize(
    "regex_value, input_str, matches, captures",
    [
        ("^match this$", "match this", True, None),
        ("^my (.+) cap", "my first cap", True, ["first"]),
        (".* (.+) - (.+) two", "my other - capped two", True, ["other", "capped"]),
        ("failed match", "nope", False, None),
    ],
)
def test_regex_validator(regex_value, input_str, matches, captures):
    regex_validator = RegexValidator(name="good_regex_validator", value=regex_value)
    assert regex_validator._name == "good_regex_validator"
    assert regex_validator._value == regex_value

    assert regex_validator.is_match(input_str=input_str) is matches
    assert regex_validator.capture(input_str=input_str) == captures


@pytest.mark.parametrize("regex_value", ["(", "??"])
def test_regex_validator_fails_bad_value(regex_value):
    with pytest.raises(ValidationException, match="Validation error in fail: invalid regex"):
        _ = RegexValidator(name="fail", value=regex_value)


def test_regex_list_validator():
    regex_list_validator_raw_value = ["try matching this", "try matching that", "how about this"]

    regex_list = RegexListValidator(name="list val", value=regex_list_validator_raw_value)

    for raw_val in regex_list_validator_raw_value:
        assert regex_list.matches_any(raw_val)
        assert regex_list.capture_any(raw_val) is None


def test_regex_list_validator_capture():
    regex_list_validator_raw_value = ["try (.+) this", "try (.+) that", "how (.+) this"]

    regex_list = RegexListValidator(name="list val", value=regex_list_validator_raw_value)
    captures_test = [
        ("try first this", "first"),
        ("try second that", "second"),
        ("how third this", "third"),
    ]

    for capture_str, expected_capture in captures_test:
        assert regex_list.matches_any(capture_str)
        assert regex_list.capture_any(capture_str) == [expected_capture]


def test_regex_list_validator_invalid_regex():
    with pytest.raises(ValidationException, match="Validation error in fail\.2: invalid regex"):
        _ = RegexListValidator(name="fail", value=["first is good", "second ( bad", "third okay"])


def test_regex_list_validator_inconsistent_capture_groups():
    with pytest.raises(
        ValidationException,
        match=(
            "Validation error in fail: "
            "each regex in a list must have the same number of capture groups"
        ),
    ):
        _ = RegexListValidator(
            name="fail",
            value=[
                "first with one (.+) cap group",
                "two (.+) has two (.) cap groups",
            ],
        )
