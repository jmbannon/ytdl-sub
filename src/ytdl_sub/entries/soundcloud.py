from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.variables.soundcloud_variables import SoundcloudVariables


class SoundcloudTrack(SoundcloudVariables, Entry):
    """
    Entry object to represent a Soundcloud track yt-dlp that is a single, which implies
    it does not belong to an album.
    """

    entry_extractor = "soundcloud"

    def is_premiere(self) -> bool:
        """
        Returns whether the entry is a premier track. Check this by seeing if the track's url is
        a preview.
        """
        return "/preview/" in self.kwargs("url")


class SoundcloudAlbumTrack(SoundcloudTrack):
    """
    Entry object to represent a Soundcloud track yt-dlp that belongs to an album.
    """

    @property
    def track_number(self) -> int:
        """Returns the entry's track number"""
        return self.kwargs("playlist_index")

    @property
    def track_count(self) -> int:
        """Returns the entry's total tracks in album"""
        return self.kwargs("playlist_count")

    @property
    def album(self) -> str:
        """Returns the entry's album name, fetched from its internal album"""
        return self.kwargs("playlist")

    @property
    def album_year(self) -> int:
        """Returns the entry's album year, fetched from its internal album"""
        # added from parent entry
        return self._additional_variables["playlist_max_upload_year"]
