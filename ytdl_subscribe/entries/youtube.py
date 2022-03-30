from ytdl_subscribe.entries.entry import Entry


class YoutubeVideo(Entry):
    @property
    def title(self) -> str:
        # Try to get the track, fall back on title
        if self.kwargs_contains('track'):
            return self.kwargs('track')

        return super(YoutubeVideo, self).title
