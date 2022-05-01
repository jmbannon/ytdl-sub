import os.path
from pathlib import Path
from typing import Optional

from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.variables.youtube_variables import YoutubeVideoVariables


class YoutubeVideo(YoutubeVideoVariables, Entry):
    """
    Entry object to represent a Youtube video.
    """

    def get_download_thumbnail_path(self) -> str:
        """
        Returns
        -------
        The entry's thumbnail's file path to where it was downloaded. Ytdl has a bug where the
        thumbnail entry is not the actual thumbnail it downloaded. So check all the possible
        extensions that it may have downloaded, and see if that thumbnail's extension exists.

        TODO: always make thumbnails jpg
        """
        thumbnails = self.kwargs("thumbnails")
        possible_thumbnail_exts = set()
        for thumbnail in thumbnails:
            possible_thumbnail_exts.add(thumbnail["url"].split(".")[-1])

        for ext in possible_thumbnail_exts:
            possible_thumbnail_path = str(Path(self.working_directory()) / f"{self.uid}.{ext}")
            if os.path.isfile(possible_thumbnail_path):
                return possible_thumbnail_path

        return super().get_download_thumbnail_path()


class YoutubePlaylistVideo(YoutubeVideo):
    @property
    def playlist_index(self) -> int:
        """
        Returns
        -------
        The playlist index
        """
        return self.kwargs("playlist_index")

    @property
    def playlist_size(self) -> int:
        """
        Returns
        -------
        The size of the playlist
        """
        return self.kwargs("playlist_count")


class YoutubeChannel(Entry):
    def _get_thumbnail_url(self, thumbnail_id: str) -> Optional[str]:
        """
        Downloads a specific thumbnail from a YTDL entry's thumbnail list

        Parameters
        ----------
        thumbnail_id:
            Id of the thumbnail defined in the channel's thumbnail

        Returns
        -------
        Desired thumbnail url if it exists. None if it does not.
        """
        for thumbnail in self.kwargs("thumbnails"):
            if thumbnail["id"] == thumbnail_id:
                return thumbnail["url"]
        return None

    def avatar_thumbnail_url(self) -> str:
        """
        Returns
        -------
        The channel's uncropped avatar image url
        """
        return self._get_thumbnail_url(thumbnail_id="avatar_uncropped")

    def banner_thumbnail_url(self) -> str:
        """
        Returns
        -------
        The channel's uncropped banner image url
        """
        return self._get_thumbnail_url(thumbnail_id="banner_uncropped")
