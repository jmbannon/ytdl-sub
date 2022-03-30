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
