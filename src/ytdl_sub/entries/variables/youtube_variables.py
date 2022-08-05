from yt_dlp.utils import sanitize_filename

from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.variables.entry_variables import EntryVariables

# This file contains mixins to a BaseEntry subclass. Ignore pylint's "no kwargs member" suggestion
# pylint: disable=no-member


class YoutubeVideoVariables(EntryVariables):
    @property
    def channel(self: BaseEntry) -> str:
        """
        Returns
        -------
        str
            The channel name.
        """
        return self.kwargs("channel")

    @property
    def channel_sanitized(self) -> str:
        """
        Returns
        -------
        str
            The channel name, sanitized.
        """
        return sanitize_filename(self.channel)

    @property
    def track_title(self: BaseEntry) -> str:
        """
        Returns
        -------
        str
            The track title of a music video if it is available, otherwise it falls back to the
            title. NOTE: Even if a video has music metadata, this variable does not always get
            pulled via yt-dlp. Use with caution.
        """
        # Try to get the track, fall back on title
        if self.kwargs_contains("track"):
            return self.kwargs("track")

        return super().title

    @property
    def track_title_sanitized(self) -> str:
        """
        Returns
        -------
        str
            The sanitized track title.
        """
        return sanitize_filename(self.track_title)

    @property
    def artist(self: BaseEntry) -> str:
        """
        Returns
        -------
        str
            The artist of a music video if it is available, otherwise it falls back to the channel.
            NOTE: Even if a video has music metadata, this variable does not always get pulled via
            yt-dlp. Use with caution.
        """
        if self.kwargs_contains("artist"):
            return self.kwargs("artist")

        return self.kwargs("channel")

    @property
    def artist_sanitized(self) -> str:
        """
        Returns
        -------
        str
            The sanitized artist name.
        """
        return sanitize_filename(self.artist)

    @property
    def playlist_index(self) -> int:
        """
        Returns
        -------
        int
            The index of the video in the playlist. For non-playlist download strategies, this will
            always return 1.
        """
        return 1

    @property
    def playlist_size(self) -> int:
        """
        Returns
        -------
        int
            The size of the playlist. For non-playlist download strategies, this will always return
            1.
        """
        return 1

    @property
    def description(self: BaseEntry) -> str:
        """
        Returns
        -------
        str
            The video description.
        """
        return self.kwargs("description")
