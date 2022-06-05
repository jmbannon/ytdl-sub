from typing import Any
from typing import Optional
from urllib.parse import parse_qs
from urllib.parse import urlparse

from ytdl_sub.validators.validators import StringValidator


class YoutubeVideoUrlValidator(StringValidator):

    _expected_value_type_name = "youtube video url"

    @classmethod
    def _get_video_id(cls, url: str) -> Optional[str]:
        """
        Examples:
        - https://youtu.be/SA2iWivDJiE
        - https://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - https://www.youtube.com/embed/SA2iWivDJiE
        - https://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        """
        # If the url doesn't contain the 'youtu' substring, assume it is the video id
        if "youtu" not in url:
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
