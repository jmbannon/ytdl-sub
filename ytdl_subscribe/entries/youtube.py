import os.path
from pathlib import Path

from ytdl_subscribe.entries.entry import Entry
from ytdl_subscribe.entries.variables.youtube_variables import YoutubeVideoVariables


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
