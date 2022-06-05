from typing import Any
from typing import Optional
from urllib.parse import parse_qs
from urllib.parse import urlparse

from ytdl_sub.validators.validators import StringValidator


class YoutubeVideoUrlValidator(StringValidator):

    _expected_value_type_name = "Youtube video url"

    @classmethod
    def _get_video_id(cls, url: str) -> Optional[str]:
        """
        Examples:
        - https://youtu.be/SA2iWivDJiE
        - https://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - https://www.youtube.com/embed/SA2iWivDJiE
        - https://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        """
        # If the url doesn't contain youtube or youtu.be, assume it is invalid
        if "youtube.com" not in url and "youtu.be" not in url:
            return None

        # If https:// is not present, urlparse will not work
        if not url.startswith("https://"):
            url = f"https://{url}"

        query = urlparse(url)
        if query.hostname in ("youtu.be", "www.youtu.be"):
            return query.path[1:]
        if query.hostname in ("youtube.com", "www.youtube.com"):
            if query.path == "/watch":
                parsed_q = parse_qs(query.query)
                return parsed_q["v"][0]
            if query.path[:7] == "/embed/":
                return query.path.split("/")[2]
            if query.path[:3] == "/v/":
                return query.path.split("/")[2]

        return None

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)

        self._video_id = self._get_video_id(value)
        if not self._video_id:
            raise self._validation_exception(f"'{value}' is not a valid Youtube video url.")

    @property
    def video_url(self) -> str:
        """
        Returns
        -------
        Full video URL
        """
        return f"https://youtube.com/watch?v={self._video_id}"


class YoutubePlaylistUrlValidator(StringValidator):

    _expected_value_type_name = "Youtube playlist url"

    @classmethod
    def _get_playlist_id(cls, url: str) -> Optional[str]:
        """
        Examples:
        - https://www.youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc
        """
        # If the url doesn't contain youtube, assume it is invalid
        if "youtube.com" not in url:
            return None

        # If https:// is not present, urlparse will not work
        if not url.startswith("https://"):
            url = f"https://{url}"

        query = urlparse(url)
        if query.hostname in ("youtube.com", "www.youtube.com"):
            if query.path == "/playlist":
                parsed_q = parse_qs(query.query)
                return parsed_q["list"][0]

        return None

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)

        self._playlist_id = self._get_playlist_id(value)
        if not self._playlist_id:
            raise self._validation_exception(f"'{value}' is not a valid Youtube playlist url.")

    @property
    def playlist_url(self) -> str:
        """
        Returns
        -------
        Full playlist URL
        """
        return f"https://youtube.com/playlist?list={self._playlist_id}"


class YoutubeChannelUrlValidator(StringValidator):

    _expected_value_type_name = "Youtube channel url"

    @classmethod
    def _get_channel_url(cls, url: str) -> Optional[str]:
        """
        Examples:
        - https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw
        - https://www.youtube.com/user/username
        - https://www.youtube.com/c/channel_name
        """
        # If the url doesn't contain youtube, assume it is invalid
        if "youtube.com" not in url:
            return None

        # If https:// is not present, urlparse will not work
        if not url.startswith("https://"):
            url = f"https://{url}"

        query = urlparse(url)
        if query.hostname in ("youtube.com", "www.youtube.com"):
            if any(query.path.startswith(qpath) for qpath in ("/channel/", "/user/", "/c/")):
                return f"https://youtube.com{query.path}"

        return None

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)

        self._channel_url = self._get_channel_url(value)
        if not self._channel_url:
            raise self._validation_exception(f"'{value}' is not a valid Youtube channel url.")

    @property
    def channel_url(self) -> str:
        """
        Returns
        -------
        Full channel URL
        """
        return self._channel_url


class SoundcloudUsernameUrlValidator(StringValidator):

    _expected_value_type_name = "Soundcloud username url"

    @classmethod
    def _get_channel_url(cls, url: str) -> Optional[str]:
        """
        Examples:
        - https://www.soundcloud.com/artist_name
        """
        # If the url doesn't contain soundcloud, assume it is invalid
        if "soundcloud.com" not in url:
            return None

        # If https:// is not present, urlparse will not work
        if not url.startswith("https://"):
            url = f"https://{url}"

        query = urlparse(url)
        if query.hostname in ("soundcloud.com", "www.soundcloud.com"):
            if len(query.path) > 2:  # /artist_name
                username = query.path[1:].split("/")[0]  # strip extra paths or slashes
                username = username.split("?")[0]  # strip extra arguments
                return f"https://soundcloud.com/{username}"

        return None

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)

        self._username_url = self._get_channel_url(value)
        if not self._username_url:
            raise self._validation_exception(f"'{value}' is not a valid Soundcloud username url.")

    @property
    def username_url(self) -> str:
        """
        Returns
        -------
        Full artist URL
        """
        return self._username_url
