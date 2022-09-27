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
