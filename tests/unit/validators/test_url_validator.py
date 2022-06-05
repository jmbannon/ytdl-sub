import pytest

from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.validators.url_validator import YoutubeVideoUrlValidator, YoutubePlaylistUrlValidator


class TestYoutubeVideoUrlValidator:
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
    def test_youtube_video_validator_success(self, url):
        video_id = YoutubeVideoUrlValidator(name="unit test", value=url).video_id
        assert video_id == "dQw4w9WgXcQ"


    def test_youtube_video_validator_fail(self):
        bad_url = "youtube.cum/asdfd"
        expected_error_msg = f"'{bad_url}' is not a valid Youtube video url or ID."
        with pytest.raises(ValidationException, match=expected_error_msg):
            YoutubeVideoUrlValidator(name="unit test", value=bad_url)


class TestYoutubePlaylistUrlValidator:
    @pytest.mark.parametrize(
        "url",
        [
            "PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
            "youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
            "www.youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
            "https://youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
            "https://www.youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
        ],
    )
    def test_youtube_video_validator_success(self, url):
        playlist_id = YoutubePlaylistUrlValidator(name="unit test", value=url).playlist_id
        assert playlist_id == "PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc"

    def test_youtube_playlist_validator_fail(self):
        bad_url = "youpoop.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc"
        expected_error_msg = f"'{bad_url}' is not a valid Youtube playlist url or ID."
        with pytest.raises(ValidationException, match=expected_error_msg):
            YoutubeVideoUrlValidator(name="unit test", value=bad_url)

class TestYoutubeChannelUrlValidator:
    @pytest.mark.parametrize(
        "url",
        [
            "PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
            "youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
            "www.youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
            "https://youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
            "https://www.youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
        ],
    )
    def test_youtube_video_validator_success(self, url):
        playlist_id = YoutubePlaylistUrlValidator(name="unit test", value=url).playlist_id
        assert playlist_id == "PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc"

    def test_youtube_playlist_validator_fail(self):
        bad_url = "youpoop.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc"
        expected_error_msg = f"'{bad_url}' is not a valid Youtube playlist url or ID."
        with pytest.raises(ValidationException, match=expected_error_msg):
            YoutubeVideoUrlValidator(name="unit test", value=bad_url)