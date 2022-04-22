import os.path
from pathlib import Path

from ytdl_subscribe.entries.entry import Entry


class YoutubeVideo(Entry):
    """
    Entry object to represent a Youtube video.
    """

    @property
    def title(self) -> str:
        """
        Returns the title of the youtube video. Tries to get the track name if it is available,
        otherwise it falls back to the title.
        """
        # Try to get the track, fall back on title
        if self.kwargs_contains("track"):
            return self.kwargs("track")

        return super().title

    @property
    def download_thumbnail_path(self) -> str:
        """
        Returns
        -------
        The entry's thumbnail's file path to where it was downloaded. Ytdl has a bug where the
        thumbnail entry is not the actual thumbnail it downloaded. So check all the possible
        extensions that it may have downloaded, and see if that thumbnail's extension exists.

        TODO: move this into the init so the thumbnail_ext variable can be set accordingly
        """
        thumbnails = self.kwargs("thumbnails")
        possible_thumbnail_exts = set()
        for thumbnail in thumbnails:
            possible_thumbnail_exts.add(thumbnail["url"].split(".")[-1])

        for ext in possible_thumbnail_exts:
            possible_thumbnail_path = str(Path(self.working_directory) / f"{self.uid}.{ext}")
            if os.path.isfile(possible_thumbnail_path):
                return possible_thumbnail_path

        return super().download_thumbnail_path
