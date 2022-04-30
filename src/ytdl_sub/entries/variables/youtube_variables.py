from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.variables.entry_variables import EntryVariables

# This file contains mixins to a BaseEntry subclass. Ignore pylint's "no kwargs member" suggestion
# pylint: disable=no-member


class YoutubeVideoVariables(EntryVariables):
    @property
    def track_title(self: BaseEntry) -> str:
        """
        Returns
        -------
        The track title of a music video if it is available, otherwise it falls back to the title.
        """
        # Try to get the track, fall back on title
        if self.kwargs_contains("track"):
            return self.kwargs("track")

        return super().title

    @property
    def playlist_index(self) -> int:
        """
        Returns
        -------
        The index of the video in the playlist. For non-playlist download strategies, this will
        always return 1.
        """
        return 1

    @property
    def playlist_size(self) -> int:
        """
        Returns
        -------
        The size of the playlist. For non-playlist download strategies, this will always return 1.
        """
        return 1
