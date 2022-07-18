import re

import pytest

from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.validators.url_validator import SoundcloudUsernameUrlValidator
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

    @pytest.mark.parametrize(
        "bad_url",
        [
            "utube.com/watch?v=sdfsadf",
            "youtube.com/nope?v=sdfsadf",
            "youtube.com",
            "youtube.com/watch",
            "youtube.com/watch?v=",
            "youtu.be/",
            "youtu.be",
        ],
    )
    def test_youtube_video_url_validator_fail(self, bad_url):
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

    @pytest.mark.parametrize(
        "bad_url",
        [
            "youpoop.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
            "youtube.com/playlistlist=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
            "youtube.com",
            "youtube.com/playlist/asdfsdfsdf",
            "youtube.com/playlist?list=",
            "youtube.com/playlist",
        ],
    )
    def test_youtube_playlist_url_validator_fail(self, bad_url):
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
            (
                "https://youtube.com/extracredits",
                "https://youtube.com/extracredits",
            ),
        ],
    )
    def test_youtube_channel_url_validator_success(self, url, expected_url):
        channel_url = YoutubeChannelUrlValidator(name="unit test", value=url).channel_url
        assert channel_url == expected_url

    @pytest.mark.parametrize(
        "bad_url",
        [
            "www.youtube.com/cha/UCuAXFkgsw1L7xaCfnd5JJOw",
            "www.nopetube.com/channel/asdfdsf",
            "www.youtube.com/channel/",
            "www.youtube.com/channell/asdfasdf",
        ],
    )
    def test_youtube_channel_url_validator_fail(self, bad_url):
        expected_error_msg = f"'{bad_url}' is not a valid Youtube channel url."
        with pytest.raises(ValidationException, match=re.escape(expected_error_msg)):
            YoutubeChannelUrlValidator(name="unit test", value=bad_url)


class TestSoundcloudUsernameUrlValidator:
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
        username_url = SoundcloudUsernameUrlValidator(name="unit test", value=url).username_url
        assert username_url == "https://soundcloud.com/poop"

    @pytest.mark.parametrize("bad_url", ["soundcloud.com", "soundnope.lol", "soundcloud.comm/"])
    def test_youtube_playlist_url_validator_fail(self, bad_url):
        expected_error_msg = f"'{bad_url}' is not a valid Soundcloud username url."
        with pytest.raises(ValidationException, match=re.escape(expected_error_msg)):
            SoundcloudUsernameUrlValidator(name="unit test", value=bad_url)
