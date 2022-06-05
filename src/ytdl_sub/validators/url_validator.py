from typing import Any
from typing import Optional
from urllib.parse import parse_qs
from urllib.parse import urlparse

from ytdl_sub.utils.exceptions import ValidationException
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
        # If the url doesn't contain youtube, assume it is the video id
        if "youtube.com" not in url and "youtu.be" not in url:
            return url

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
            raise self._validation_exception(f"'{value}' is not a valid Youtube video url or ID.")

    @property
    def video_id(self) -> str:
        """
        Returns
        -------
        ID of the video
        """
        return self._video_id


class YoutubePlaylistUrlValidator(StringValidator):

    _expected_value_type_name = "Youtube playlist url"

    @classmethod
    def _get_playlist_id(cls, url: str) -> Optional[str]:
        """
        Examples:
        - https://www.youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc
        """
        # If the url doesn't contain youtube, assume it is the ID
        if "youtube.com" not in url:
            return url

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
            raise self._validation_exception(f"'{value}' is not a valid Youtube playlist url or ID.")

    @property
    def playlist_id(self) -> str:
        """
        Returns
        -------
        ID of the channel
        """
        return self._playlist_id


class YoutubeChannelUrlValidator(StringValidator):

    _expected_value_type_name = "Youtube channel url"

    @classmethod
    def _get_channel_id(cls, url: str) -> Optional[str]:
        """
        Examples:
        - https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw

        NOT:
        - https://www.youtube.com/user/a_username_that_can_change
        - https://www.youtube.com/c/a_name_that_can_change

        Raises
        ------
        ValidationException
            If the url is for the user name
        """
        # If the url doesn't contain youtube, assume it is the ID
        if "youtube.com" not in url:
            return url

        # If https:// is not present, urlparse will not work
        if not url.startswith("https://"):
            url = f"https://{url}"

        query = urlparse(url)
        if query.hostname in ("youtube.com", "www.youtube.com"):
            if query.path == "/channel":
                parsed_q = parse_qs(query.query)
                return parsed_q["v"][0]
            if query.path in ("/user", "/c"):
                raise ValidationException('user or c not allowed since it can change')

        return None

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)

        try:
            self._channel_id = self._get_channel_id(value)
        except ValidationException:
            raise self._validation_exception(
                f"{value} uses a deprecated Youtube url that which can change. "
                f"Use the /channel/ url instead."
            )

        if not self._channel_id:
            raise self._validation_exception(f"'{value}' is not a valid Youtube channel url or ID.")

    @property
    def channel_id(self) -> str:
        """
        Returns
        -------
        ID of the channel
        """
        return self._channel_id
