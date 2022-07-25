import pytest

from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.validators.regex_validator import RegexListValidator
from ytdl_sub.validators.regex_validator import RegexValidator


@pytest.mark.parametrize(
    "regex_value, input_str, expected_output",
    [
        ("^match this$", "match this", []),
        ("^my (.+) cap", "my first cap", ["first"]),
        (".* (.+) - (.+) two", "my other - capped two", ["other", "capped"]),
        ("failed match", "nope", None),
    ],
)
def test_regex_validator(regex_value, input_str, expected_output):
    regex_validator = RegexValidator(name="good_regex_validator", value=regex_value)
    assert regex_validator._name == "good_regex_validator"
    assert regex_validator._value == regex_value

    assert regex_validator.match(input_str=input_str) == expected_output


@pytest.mark.parametrize("regex_value", ["(", "??"])
def test_regex_validator_fails_bad_value(regex_value):
    with pytest.raises(ValidationException, match="Validation error in fail: invalid regex"):
        _ = RegexValidator(name="fail", value=regex_value)


def test_regex_list_validator_matches():
    regex_list_validator_raw_value = ["try matching this", "try matching that", "how about this"]

    regex_list = RegexListValidator(name="list val", value=regex_list_validator_raw_value)

    for raw_val in regex_list_validator_raw_value:
        assert regex_list.match_any(raw_val) == []


def test_regex_list_with_string_value():
    regest_list_with_string_value = "try matching this"
    regex_list = RegexListValidator(name="list val", value=regest_list_with_string_value)
    assert regex_list.match_any(regest_list_with_string_value) == []


def test_regex_list_validator_captures():
    regex_list_validator_raw_value = ["try (.+) this", "try (.+) that", "how (.+) this"]

    regex_list = RegexListValidator(name="list val", value=regex_list_validator_raw_value)
    captures_test = [
        ("try first this", "first"),
        ("try second that", "second"),
        ("how third this", "third"),
    ]

    for capture_str, expected_capture in captures_test:
        assert regex_list.match_any(capture_str) == [expected_capture]


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
