import pytest

from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.validators.url_validator import YoutubeVideoUrlValidator


@pytest.mark.parametrize(
    "url",
    [
        "dQw4w9WgXcQ",
        "youtu.be/dQw4w9WgXcQ",
        "www.youtu.be/dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=feedu",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://www.youtube.com/v/dQw4w9WgXcQ?version=3&amp;hl=en_US",
    ],
)
def test_youtube_video_validator_success(url):
    video_id = YoutubeVideoUrlValidator(name="unit test", value=url).video_id
    assert video_id == "dQw4w9WgXcQ"


def test_youtube_video_validator_fail():
    bad_url = "youtube.cum/asdfd"
    expected_error_msg = f"'{bad_url}' is not a valid Youtube video url or ID."
    with pytest.raises(ValidationException, match=expected_error_msg):
        YoutubeVideoUrlValidator(name="unit test", value=bad_url)
