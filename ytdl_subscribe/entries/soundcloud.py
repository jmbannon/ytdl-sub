from typing import List, Type, Dict

from sanitize_filename import sanitize

from ytdl_subscribe.entries.entry import Entry


class SoundcloudTrack(Entry):
    @property
    def upload_date(self) -> str:
        return self.kwargs("upload_date")

    @property
    def upload_year(self) -> int:
        return int(self.upload_date[:4])

    @property
    def thumbnail(self) -> str:
        return self.kwargs("thumbnail")

    @property
    def thumbnail_ext(self) -> str:
        return self.thumbnail.split(".")[-1]

    @property
    def track_number(self) -> int:
        return 1

    @property
    def track_number_padded(self) -> str:
        return f"{self.track_number:02d}"

    @property
    def album(self) -> str:
        return self.title

    @property
    def sanitized_album(self) -> str:
        return sanitize(self.album)

    @property
    def album_year(self) -> int:
        return self.upload_year

    @property
    def is_premiere(self) -> bool:
        return "/preview/" in self.kwargs("url")

    def to_dict(self) -> Dict:
        return dict(
            super(SoundcloudTrack, self).to_dict(),
            **{
                "upload_date": self.upload_date,
                "upload_year": self.upload_year,
                "thumbnail": self.thumbnail,
                "thumbnail_ext": self.thumbnail_ext,
                "track_number": self.track_number,
                "track_number_padded": self.track_number_padded,
                "album": self.album,
                "sanitized_album": self.sanitized_album,
                "album_year": self.album_year,
                "is_premiere": self.is_premiere,
            },
        )


class SoundcloudAlbumTrack(SoundcloudTrack):
    def __init__(self, album, track_number, **kwargs):
        super(SoundcloudAlbumTrack, self).__init__(**kwargs)
        self._album = album
        self._track_number = track_number

    @property
    def track_number(self) -> int:
        return self._track_number

    @property
    def album(self) -> str:
        return self._album.title

    @property
    def album_year(self) -> int:
        return self._album.album_year

class SoundcloudAlbum(Entry):
    def __init__(self, skip_premiere_tracks: bool, **kwargs):
        super(SoundcloudAlbum, self).__init__(**kwargs)
        self.skip_premiere_tracks = skip_premiere_tracks

    @property
    def album_tracks(self) -> List[SoundcloudAlbumTrack]:
        tracks = [
            SoundcloudAlbumTrack(album=self, track_number=i + 1, **entry)
            for i, entry in enumerate(self.kwargs("entries"))
        ]
        if self.skip_premiere_tracks:
            tracks = [t for t in tracks if not t.is_premiere]

        return tracks

    @property
    def album_year(self) -> int:
        return min([track.upload_year for track in self.album_tracks])

    def contains(self, track: SoundcloudTrack) -> bool:
        return any([track.uid == t.uid for t in self.album_tracks])
