from typing import Dict
from typing import List

from ytdl_sub.entries.base_entry import PlaylistMetadata
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.variables.soundcloud_variables import SoundcloudVariables


class SoundcloudTrack(SoundcloudVariables, Entry):
    """
    Entry object to represent a Soundcloud track yt-dlp that is a single, which implies
    it does not belong to an album.
    """

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
        album: str,
        album_year: int,
        playlist_metadata: PlaylistMetadata,
    ):
        """
        Initialize the album track using album metadata and ytdl metadata for the specific track.
        """
        super().__init__(entry_dict=entry_dict, working_directory=working_directory)
        self._album = album
        self._album_year = album_year
        self._playlist_metadata = playlist_metadata

    @property
    def track_number(self) -> int:
        """Returns the entry's track number"""
        return self._playlist_metadata.playlist_index

    @property
    def album(self) -> str:
        """Returns the entry's album name, fetched from its internal album"""
        return self._album

    @property
    def track_count(self) -> int:
        """Returns the entry's total tracks in album for singles this is 1"""
        return self._playlist_metadata.playlist_count

    @property
    def album_year(self) -> int:
        """Returns the entry's album year, fetched from its internal album"""
        return self._album_year

    @classmethod
    def from_soundcloud_track(
        cls,
        album: str,
        album_year: int,
        soundcloud_track: SoundcloudTrack,
        playlist_metadata: PlaylistMetadata,
    ) -> "SoundcloudAlbumTrack":
        """
        Parameters
        ----------
        album:
            Album name
        album_year:
            Album year
        soundcloud_track:
            Track to convert to an album track
        playlist_metadata:
            Metadata for playlist ordering

        Returns
        -------
        SoundcloudTrack converted to a SoundcloudAlbumTrack
        """
        return SoundcloudAlbumTrack(
            entry_dict=soundcloud_track._kwargs,  # pylint: disable=protected-access
            working_directory=soundcloud_track.working_directory(),
            album=album,
            album_year=album_year,
            playlist_metadata=playlist_metadata,
        )


class SoundcloudAlbum(Entry):
    """
    Entry object to represent a Soundcloud album.
    """

    @property
    def _single_tracks(self) -> List[SoundcloudTrack]:
        """
        Returns all tracks in the album represented by singles. Use this to fetch any
        data needed from the tracks before representing it as an album track.
        """
        return [
            SoundcloudTrack(entry_dict=entry, working_directory=self._working_directory)
            for entry in self.kwargs("entries")
        ]

    def album_tracks(self, skip_premiere_tracks: bool = True) -> List[SoundcloudAlbumTrack]:
        """
        Returns
        -------
        All tracks in the album represented as album-tracks. They will share the
        same album name, have ordered track numbers, and a shared album year.
        """
        tracks = [
            track
            for track in self._single_tracks
            if not (skip_premiere_tracks and track.is_premiere())
        ]

        album_tracks = [
            SoundcloudAlbumTrack.from_soundcloud_track(
                album=self.title,
                album_year=self.album_year,
                soundcloud_track=track,
                playlist_metadata=PlaylistMetadata(
                    playlist_id=self.uid,
                    playlist_extractor=self.extractor,
                    playlist_index=track.kwargs("playlist_index"),
                    playlist_count=self.track_count,
                ),
            )
            for track in tracks
        ]

        return album_tracks

    @property
    def album_year(self) -> int:
        """
        Returns
        -------
        The album's year, computed by the max upload year amongst all album tracks
        """
        return max(track.upload_year for track in self._single_tracks)

    @property
    def track_count(self) -> int:
        """
        Returns
        -------
        Number of tracks in the album (technically a playlist)
        """
        return self.kwargs("playlist_count")

    def contains(self, track: SoundcloudTrack) -> bool:
        """
        Returns
        -------
        True if this album contains this track. False otherwise.
        """
        return any(track.uid == t.uid for t in self._single_tracks)
