from yt_dlp.utils import sanitize_filename

from ytdl_sub.entries.variables.entry_variables import EntryVariables

# This file contains mixins to a BaseEntry subclass. Ignore pylint's "no kwargs member" suggestion
# pylint: disable=no-member


class SoundcloudVariables(EntryVariables):
    @property
    def track_number(self) -> int:
        """
        Returns
        -------
        int
            The entry's track number within an album. For singles, it will always be 1.
        """
        return 1

    @property
    def track_number_padded(self) -> str:
        """
        Returns
        -------
        str
            The entry's track number, padded two digits.
        """
        return f"{self.track_number:02d}"

    @property
    def track_count(self) -> int:
        """
        Returns
        -------
        int
            The total tracks in album. For singles, it will always be 1.
        """
        return 1

    @property
    def album(self) -> str:
        """
        Returns
        -------
        str
            The entry's album name. For singles, it will be the same as the title.
        """
        return self.title

    @property
    def album_sanitized(self) -> str:
        """
        Returns
        -------
        str
            The entry's sanitized album name, which is safe to use for Unix and Windows file names.
        """
        return sanitize_filename(self.album)

    @property
    def album_year(self) -> int:
        """
        Returns
        -------
        int
            The entry's album year, which is determined by the latest year amongst all tracks in the
            album.
        """
        return self.upload_year
