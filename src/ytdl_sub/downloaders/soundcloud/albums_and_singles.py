from typing import Dict
from typing import Generator
from typing import List

from ytdl_sub.downloaders.downloader import download_logger
from ytdl_sub.downloaders.soundcloud.abc import SoundcloudDownloader
from ytdl_sub.downloaders.soundcloud.abc import SoundcloudDownloaderOptions
from ytdl_sub.entries.soundcloud import SoundcloudAlbum
from ytdl_sub.entries.soundcloud import SoundcloudAlbumTrack
from ytdl_sub.entries.soundcloud import SoundcloudTrack
from ytdl_sub.validators.url_validator import SoundcloudUsernameUrlValidator


class SoundcloudAlbumsAndSinglesDownloadOptions(SoundcloudDownloaderOptions):
    """
    Downloads a soundcloud user's entire discography. Groups together album tracks and considers
    any track not in an album as a single. Also includes any collaboration tracks.

    Usage:

    .. code-block:: yaml

      presets:
        my_example_preset:
          soundcloud:
            # required
            download_strategy: "albums_and_singles"
            url: "soundcloud.com/username"
            # optional
            skip_premiere_tracks: True

    """

    _required_keys = {"url"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._url = self._validate_key(
            key="url", validator=SoundcloudUsernameUrlValidator
        ).username_url

    @property
    def url(self) -> str:
        """
        Required. The Soundcloud user's url, i.e. ``soundcloud.com/the_username``
        """
        return self._url


class SoundcloudAlbumsAndSinglesDownloader(
    SoundcloudDownloader[SoundcloudAlbumsAndSinglesDownloadOptions]
):
    downloader_options_type = SoundcloudAlbumsAndSinglesDownloadOptions
    supports_subtitles = False
    supports_chapters = False

    @classmethod
    def ytdl_option_defaults(cls) -> Dict:
        """
        Default `ytdl_options`_ for ``albums_and_singles``

        .. code-block:: yaml

           ytdl_options:
             ignoreerrors: True  # ignore errors like hidden videos, age restriction, etc
             format: "bestaudio[ext=mp3]"  # download format the best possible mp3
        """
        return dict(
            super().ytdl_option_defaults(),
            **{
                "format": "bestaudio[ext=mp3]",
            },
        )

    def _get_albums_from_entry_dicts(self, entry_dicts: List[Dict]) -> List[SoundcloudAlbum]:
        """
        Parameters
        ----------
        entry_dicts
            Entry dicts from extracting info jsons

        Returns
        -------
        Dict containing album_id: album class
        """
        albums: Dict[str, SoundcloudAlbum] = {}

        # First, get the albums themselves
        for entry_dict in self._filter_entry_dicts(entry_dicts, extractor="soundcloud:set"):
            albums[entry_dict["id"]] = SoundcloudAlbum(
                entry_dict=entry_dict, working_directory=self.working_directory
            )

        # Then, get all tracks that belong to the album
        for entry_dict in self._filter_entry_dicts(entry_dicts):
            album_id = entry_dict.get("playlist_id")
            if album_id in albums:
                albums[album_id].tracks.append(
                    SoundcloudTrack(entry_dict=entry_dict, working_directory=self.working_directory)
                )

        return list(albums.values())

    def _get_singles(
        self, entry_dicts: List[Dict], albums: List[SoundcloudAlbum]
    ) -> List[SoundcloudTrack]:
        tracks: List[SoundcloudTrack] = []

        # Get all tracks that are not part of an album
        for entry_dict in self._filter_entry_dicts(entry_dicts):
            if not any(entry_dict in album for album in albums):
                tracks.append(
                    SoundcloudTrack(entry_dict=entry_dict, working_directory=self.working_directory)
                )

        return tracks

    def _get_albums(self) -> List[SoundcloudAlbum]:
        # Dry-run to get the info json files
        artist_albums_url = self.artist_albums_url(artist_url=self.download_options.url)
        album_entry_dicts = self.extract_info_via_info_json(
            only_info_json=True,
            log_prefix_on_info_json_dl="Downloading metadata for",
            url=artist_albums_url,
        )

        albums = self._get_albums_from_entry_dicts(entry_dicts=album_entry_dicts)
        return albums

    def _get_album_tracks(
        self, albums: List[SoundcloudAlbum]
    ) -> Generator[SoundcloudAlbumTrack, None, None]:
        for album in albums:
            if len(album.album_tracks()) > 0:
                download_logger.info("Downloading album %s", album.title)

            for track in album.album_tracks():
                if self.download_options.skip_premiere_tracks and track.is_premiere():
                    continue

                download_logger.info(
                    "Downloading album track %d/%d %s",
                    track.track_number,
                    track.track_count,
                    track.title,
                )
                if not self.is_dry_run:
                    _ = self.extract_info_with_retry(
                        is_downloaded_fn=track.is_downloaded,
                        url=album.webpage_url,
                        ytdl_options_overrides={
                            "playlist_items": str(track.kwargs("playlist_index")),
                            "writeinfojson": False,
                        },
                    )

                yield track

    def _get_single_tracks(
        self, albums: List[SoundcloudAlbum]
    ) -> Generator[SoundcloudTrack, None, None]:
        artist_tracks_url = self.artist_tracks_url(artist_url=self.download_options.url)
        tracks_entry_dicts = self.extract_info_via_info_json(
            only_info_json=True,
            log_prefix_on_info_json_dl="Downloading metadata for",
            url=artist_tracks_url,
        )

        # Then, get all singles
        tracks = self._get_singles(entry_dicts=tracks_entry_dicts, albums=albums)
        for track in tracks:
            # Filter any premiere tracks if specified
            if self.download_options.skip_premiere_tracks and track.is_premiere():
                continue

            download_logger.info("Downloading single track %s", track.title)
            if not self.is_dry_run:
                _ = self.extract_info_with_retry(
                    is_downloaded_fn=track.is_downloaded,
                    url=track.webpage_url,
                    ytdl_options_overrides={"writeinfojson": False},
                )

            yield track

    def download(self) -> Generator[SoundcloudTrack, None, None]:
        """
        Soundcloud subscription to download albums and tracks as singles.
        """
        albums = self._get_albums()
        for album_track in self._get_album_tracks(albums=albums):
            yield album_track

        for single_track in self._get_single_tracks(albums=albums):
            yield single_track
