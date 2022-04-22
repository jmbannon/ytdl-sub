from typing import Dict
from typing import List
from typing import Optional

from yt_dlp.utils import sanitize_filename

from ytdl_subscribe.entries.entry import Entry
from ytdl_subscribe.entries.entry import PlaylistMetadata


class SoundcloudTrack(Entry):
    """
    Entry object to represent a Soundcloud track yt-dlp that is a single, which implies
    it does not belong to an album.
    """

    @property
    def track_number(self) -> int:
        """Returns the entry's track number. Since this is a single, it will always be 1"""
        return 1

    @property
    def track_number_padded(self) -> str:
        """Returns the entry's padded track number, to the tens-place"""
        return f"{self.track_number:02d}"

    @property
    def album(self) -> str:
        """Returns the entry's album name. Since this is a single, set the album to the title"""
        return self.title

    @property
    def sanitized_album(self) -> str:
        """Returns the entry's sanitized album name"""
        return sanitize_filename(self.album)

    @property
    def album_year(self) -> int:
        """Returns the entry's album year. Since this is a single, use the upload year"""
        return self.upload_year

    @property
    def is_premiere(self) -> bool:
        """
        Returns whether the entry is a premier track. Check this by seeing if the track's url is
        a preview.
        """
        return "/preview/" in self.kwargs("url")

    def to_dict(self) -> Dict:
        """Returns the entry's values as a dictionary."""
        return dict(
            super().to_dict(),
            **{
                "track_number": self.track_number,
                "track_number_padded": self.track_number_padded,
                "album": self.album,
                "sanitized_album": self.sanitized_album,
                "album_year": self.album_year,
                "is_premiere": self.is_premiere,
            },
        )


class SoundcloudAlbumTrack(SoundcloudTrack):
    """
    Entry object to represent a Soundcloud track yt-dlp that belongs to an album.
    """

    def __init__(
        self,
        working_directory: str,
        album: str,
        album_year: int,
        playlist_metadata: PlaylistMetadata,
        **kwargs,
    ):
        """
        Initialize the album track using album metadata and ytdl metadata for the specific track.
        """
        super().__init__(working_directory=working_directory, **kwargs)
        self._album = album
        self._album_year = album_year
        self._playlist_metadata = playlist_metadata

    @property
    def playlist_metadata(self) -> Optional[PlaylistMetadata]:
        return self._playlist_metadata

    @property
    def track_number(self) -> int:
        """Returns the entry's track number"""
        return self._playlist_metadata.playlist_index

    @property
    def album(self) -> str:
        """Returns the entry's album name, fetched from its internal album"""
        return self._album

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
        return SoundcloudAlbumTrack(
            working_directory=soundcloud_track.working_directory,
            album=album,
            album_year=album_year,
            playlist_metadata=playlist_metadata,
            **soundcloud_track._kwargs,  # pylint: disable=protected-access
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
            SoundcloudTrack(working_directory=self._working_directory, **entry)
            for entry in self.kwargs("entries")
        ]

    def album_tracks(self, skip_premiere_tracks: bool = True) -> List[SoundcloudAlbumTrack]:
        """
        Returns all tracks in the album represented as album-tracks. They will share the
        same album name, have ordered track numbers, and a shared album year.
        """
        tracks = [
            track
            for track in self._single_tracks
            if not (skip_premiere_tracks and track.is_premiere)
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
                ),
            )
            for track in tracks
        ]

        return album_tracks

    @property
    def album_year(self) -> int:
        """Returns the album's year, computed by the max upload year amongst all album tracks"""
        return max(track.upload_year for track in self._single_tracks)

    @property
    def track_count(self) -> int:
        return self.kwargs("playlist_count")

    @property
    def downloaded_track_count(self) -> int:
        return len(self.kwargs("entries"))

    def contains(self, track: SoundcloudTrack) -> bool:
        """Returns whether the album contains a track"""
        return any(track.uid == t.uid for t in self._single_tracks)
