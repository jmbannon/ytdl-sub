import re

import pytest

from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.validators.url_validator import SoundcloudArtistUrlValidator
from ytdl_sub.validators.url_validator import YoutubeChannelUrlValidator
from ytdl_sub.validators.url_validator import YoutubePlaylistUrlValidator
from ytdl_sub.validators.url_validator import YoutubeVideoUrlValidator


class TestYoutubeVideoUrlValidator:
    @pytest.mark.parametrize(
        "url",
        [
            "youtu.be/dQw4w9WgXcQ",
            "www.youtu.be/dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=feedu",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/v/dQw4w9WgXcQ?version=3&amp;hl=en_US",
        ],
    )
    def test_youtube_video_url_validator_success(self, url):
        video_url = YoutubeVideoUrlValidator(name="unit test", value=url).video_url
        assert video_url == "https://youtube.com/watch?v=dQw4w9WgXcQ"

    def test_youtube_video_url_validator_fail(self):
        bad_url = "youtube.cum/asdfd"
        expected_error_msg = f"'{bad_url}' is not a valid Youtube video url."
        with pytest.raises(ValidationException, match=re.escape(expected_error_msg)):
            YoutubeVideoUrlValidator(name="unit test", value=bad_url)


class TestYoutubePlaylistUrlValidator:
    @pytest.mark.parametrize(
        "url",
        [
            "youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
            "www.youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
            "https://youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
            "https://www.youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
        ],
    )
    def test_youtube_playlist_url_validator_success(self, url):
        playlist_url = YoutubePlaylistUrlValidator(name="unit test", value=url).playlist_url
        assert (
            playlist_url == "https://youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc"
        )

    def test_youtube_playlist_url_validator_fail(self):
        bad_url = "youpoop.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc"
        expected_error_msg = f"'{bad_url}' is not a valid Youtube playlist url."
        with pytest.raises(ValidationException, match=re.escape(expected_error_msg)):
            YoutubePlaylistUrlValidator(name="unit test", value=bad_url)


class TestYoutubeChannelUrlValidator:
    @pytest.mark.parametrize(
        "url, expected_url",
        [
            (
                "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
                "https://youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
            ),
            (
                "https://youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
                "https://youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
            ),
            (
                "youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
                "https://youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
            ),
            (
                "www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
                "https://youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
            ),
            (
                "https://www.youtube.com/c/RickastleyCoUkOfficial",
                "https://youtube.com/c/RickastleyCoUkOfficial",
            ),
            (
                "https://www.youtube.com/user/videogamedunkey",
                "https://youtube.com/user/videogamedunkey",
            ),
        ],
    )
    def test_youtube_channel_url_validator_success(self, url, expected_url):
        channel_url = YoutubeChannelUrlValidator(name="unit test", value=url).channel_url
        assert channel_url == expected_url

    def test_youtube_channel_url_validator_fail(self):
        bad_url = "www.youtube.com/cha/UCuAXFkgsw1L7xaCfnd5JJOw"
        expected_error_msg = f"'{bad_url}' is not a valid Youtube channel url."
        with pytest.raises(ValidationException, match=re.escape(expected_error_msg)):
            YoutubeChannelUrlValidator(name="unit test", value=bad_url)


class TestSoundcloudArtistUrlValidator:
    @pytest.mark.parametrize(
        "url",
        [
            "soundcloud.com/poop",
            "www.soundcloud.com/poop",
            "https://soundcloud.com/poop",
            "https://www.soundcloud.com/poop",
            "https://www.soundcloud.com/poop/albums",
            "https://www.soundcloud.com/poop?link=clipboard_share",
        ],
    )
    def test_soundcloud_artist_url_validator_success(self, url):
        artist_url = SoundcloudArtistUrlValidator(name="unit test", value=url).artist_url
        assert artist_url == "https://soundcloud.com/poop"

    def test_youtube_playlist_url_validator_fail(self):
        bad_url = "soundcloud.com"
        expected_error_msg = f"'{bad_url}' is not a valid Soundcloud artist url."
        with pytest.raises(ValidationException, match=re.escape(expected_error_msg)):
            SoundcloudArtistUrlValidator(name="unit test", value=bad_url)
