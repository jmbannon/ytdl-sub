import os.path
from pathlib import Path
from typing import Optional

from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.variables.youtube_variables import YoutubeVideoVariables


class YoutubeVideo(YoutubeVideoVariables, Entry):
    """
    Entry object to represent a Youtube video. Reserved for shared Youtube entry logic.
    """

    entry_extractor = "youtube"

    @property
    def ext(self) -> str:
        """
        With ffmpeg installed, yt-dlp will sometimes merge the file into an mkv file.
        This is not reflected in the entry. See if the mkv file exists and return "mkv" if so,
        otherwise, return the original extension.
        """
        mkv_file_path = str(Path(self.working_directory()) / f"{self.uid}.mkv")
        if os.path.isfile(mkv_file_path):
            return "mkv"
        return super().ext


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
    entry_extractor = "youtube:tab"

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
