import os.path
from pathlib import Path
from typing import List, Dict

from ytdl_sub.entries.base_entry import PlaylistMetadata
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.variables.youtube_variables import YoutubeVideoVariables


class YoutubeVideo(YoutubeVideoVariables, Entry):
    """
    Entry object to represent a Youtube video.
    """

    def get_download_thumbnail_path(self) -> str:
        """
        Returns
        -------
        The entry's thumbnail's file path to where it was downloaded. Ytdl has a bug where the
        thumbnail entry is not the actual thumbnail it downloaded. So check all the possible
        extensions that it may have downloaded, and see if that thumbnail's extension exists.

        TODO: always make thumbnails jpg
        """
        thumbnails = self.kwargs("thumbnails")
        possible_thumbnail_exts = set()
        for thumbnail in thumbnails:
            possible_thumbnail_exts.add(thumbnail["url"].split(".")[-1])

        for ext in possible_thumbnail_exts:
            possible_thumbnail_path = str(Path(self.working_directory()) / f"{self.uid}.{ext}")
            if os.path.isfile(possible_thumbnail_path):
                return possible_thumbnail_path

        return super().get_download_thumbnail_path()


class YoutubePlaylistVideo(YoutubeVideo):
    def __init__(
        self,
        entry_dict: Dict,
        working_directory: str,
        playlist_metadata: PlaylistMetadata,
    ):
        """
        Initialize the playlist video with playlist metadata
        """
        super().__init__(entry_dict=entry_dict, working_directory=working_directory)
        self._playlist_metadata = playlist_metadata

    @classmethod
    def from_youtube_video(
        cls,
        youtube_video: YoutubeVideo,
        playlist_metadata: PlaylistMetadata,
    ) -> "YoutubePlaylistVideo":
        """
        Parameters
        ----------
        youtube_video:
            Video to convert to an playlist video
        playlist_metadata:
            Metadata for playlist ordering

        Returns
        -------
        YoutubeVideo converted to a YoutubePlaylistVideo
        """
        return YoutubePlaylistVideo(
            entry_dict=youtube_video._kwargs,  # pylint: disable=protected-access
            working_directory=youtube_video.working_directory(),
            playlist_metadata=playlist_metadata,
        )

    @property
    def playlist_index(self) -> int:
        """
        Returns
        -------
        The playlist index
        """
        return self._playlist_metadata.playlist_index

    @property
    def playlist_size(self) -> int:
        """
        Returns
        -------
        The size of the playlist
        """
        return self._playlist_metadata.playlist_count


class YoutubePlaylist(Entry):
    @property
    def _videos(self) -> List[YoutubeVideo]:
        """
        Returns all videos in the playlist represented by non-playlist Videos. Use this to fetch any
        data needed from the videos before representing it as a playlist video.
        """
        return [
            YoutubeVideo(entry_dict=entry, working_directory=self._working_directory)
            for entry in self.kwargs("entries")
        ]

    def playlist_videos(self) -> List[YoutubePlaylistVideo]:
        """
        Returns
        -------
        All videos in the playlist represented as YoutubePlaylistVideos. This updates
        playlist-specific fields like playlist_index and playlist_size with its actual value.
        """
        return [
            YoutubePlaylistVideo.from_youtube_video(
                youtube_video=video,
                playlist_metadata=PlaylistMetadata(
                    playlist_id=self.uid,
                    playlist_extractor=self.extractor,
                    playlist_index=video.kwargs("playlist_index"),
                    playlist_count=self.kwargs('playlist_count'),
                ),
            )
            for video in self._videos
        ]
