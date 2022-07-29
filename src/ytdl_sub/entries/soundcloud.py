from typing import Dict
from typing import List
from typing import Optional

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

    def __init__(
        self,
        entry_dict: Dict,
        working_directory: str,
        album_year: int,
    ):
        """
        Initialize the album track using album metadata and ytdl metadata for the specific track.
        """
        super().__init__(entry_dict=entry_dict, working_directory=working_directory)
        self._album_year = album_year

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
        return self._album_year

    @classmethod
    def from_soundcloud_track(
        cls,
        album_year: int,
        soundcloud_track: SoundcloudTrack,
    ) -> "SoundcloudAlbumTrack":
        """
        Parameters
        ----------
        album_year:
            Album year
        soundcloud_track:
            Track to convert to an album track

        Returns
        -------
        SoundcloudTrack converted to a SoundcloudAlbumTrack
        """
        return SoundcloudAlbumTrack(
            entry_dict=soundcloud_track._kwargs,  # pylint: disable=protected-access
            working_directory=soundcloud_track.working_directory(),
            album_year=album_year,
        )


class SoundcloudAlbum(Entry):
    """
    Entry object to represent a Soundcloud album.
    """

    entry_extractor = "soundcloud:set"

    def __init__(self, entry_dict: Dict, working_directory: Optional[str] = None):
        """
        Initialize the entry using ytdl metadata

        Parameters
        ----------
        entry_dict
            Entry metadata
        working_directory
            Optional. Directory that the entry is downloaded to
        """
        super().__init__(entry_dict=entry_dict, working_directory=working_directory)
        self.tracks: List[SoundcloudTrack] = []

    def album_tracks(self) -> List[SoundcloudAlbumTrack]:
        """
        Returns
        -------
        All tracks in the album represented as album-tracks. They will share the
        same album name, have ordered track numbers, and a shared album year.
        """
        album_tracks = [
            SoundcloudAlbumTrack.from_soundcloud_track(
                album_year=self.album_year, soundcloud_track=track
            )
            for track in self.tracks
        ]

        return sorted(album_tracks, key=lambda track: track.track_number)

    @property
    def album_year(self) -> int:
        """
        Returns
        -------
        The album's year, computed by the max upload year amongst all album tracks
        """
        return max(track.upload_year for track in self.tracks)

    @property
    def track_count(self) -> int:
        """
        Returns
        -------
        Number of tracks in the album (technically a playlist)
        """
        return self.kwargs("playlist_count")

    def __contains__(self, item):
        """
        Returns
        -------
        True if the the item (entry_dict) has the same id as one of the tracks. False otherwise.
        """
        if isinstance(item, dict):
            return any(item.get("id") == track.uid for track in self.tracks)
        return False
