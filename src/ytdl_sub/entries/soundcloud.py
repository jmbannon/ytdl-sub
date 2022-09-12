from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.variables.soundcloud_variables import SoundcloudVariables

# TODO: Delete since not used


class SoundcloudTrack(SoundcloudVariables, Entry):
    """
    Entry object to represent a Soundcloud track yt-dlp that is a single, which implies
    it does not belong to an album.
    """

    entry_extractor = "soundcloud"
