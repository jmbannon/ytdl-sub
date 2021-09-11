import json
import os
from shutil import copyfile

import music_tag
from sanitize_filename import sanitize
import dicttoxml

from PIL import Image
from ytdl_subscribe import SubscriptionSource

import yt_dlp as ytdl


def _f(value, entry):
    return value.format(**entry)


def _ffile(file_value, path, entry, makedirs=False):
    file_name = _f(file_value, entry)
    output_file_path = f"{path}/{file_name}"
    if makedirs:
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    return output_file_path


class Subscription(object):
    WORKING_DIRECTORY = ""

    source = None

    def __init__(self, name, options, ytdl_opts, post_process, overrides, output_path):
        """
        Parameters
        ----------
        name: str
            Name of the subscription
        options: dict
            Dictionary of ytdl options, specific to the source type
        ytdl_opts: dict
            Dictionary of options passed directly to ytdl. See `youtube_dl.YoutubeDL.YoutubeDL` for options.
        post_process: dict
            Dictionary of ytdl-subscribe post processing options
        overrides: dict
            Dictionary that overrides every ytdl entry. Be careful what you override!
        output_path: str
            Base path to save files to
        """
        self.name = name
        self.options = options
        self.ytdl_opts = ytdl_opts or dict()
        self.post_process = post_process
        self.overrides = overrides
        self.output_path = output_path

        # Separate each subscription's working directory
        self.WORKING_DIRECTORY += f"{'/' if self.WORKING_DIRECTORY else ''}{self.name}"

        # Always set outtmpl to the id and extension. Will be renamed using the subscription's output_path value
        self.ytdl_opts["outtmpl"] = self.WORKING_DIRECTORY + "/%(id)s.%(ext)s"
        self.ytdl_opts["writethumbnail"] = True

    def parse_entry(self, entry):
        # Add overrides to the entry
        entry = dict(entry, **self.overrides)

        # Add the file path to the entry, assert it exists
        entry["file_path"] = f"{self.WORKING_DIRECTORY}/{entry['id']}.{entry['ext']}"

        # Add sanitized values
        entry["sanitized_artist"] = sanitize(entry["artist"])
        entry["sanitized_title"] = sanitize(entry["title"])

        return entry

    def _post_process_tagging(self, entry):
        t = music_tag.load_file(entry["file_path"])
        for tag, tag_formatter in self.post_process["tagging"].items():
            t[tag] = _f(tag_formatter, entry)
        t.save()

    def _post_process_nfo(self, entry):
        nfo = {}
        for tag, tag_formatter in self.post_process["nfo"].items():
            nfo[tag] = _f(tag_formatter, entry)

        xml = dicttoxml.dicttoxml(
            obj=nfo,
            root="nfo_root" in self.post_process,
            custom_root=self.post_process.get("nfo_root"),
            attr_type=False,
        )
        nfo_file_path = _ffile(
            self.post_process["nfo_name"], self.output_path, entry, makedirs=True
        )
        with open(nfo_file_path, "wb") as f:
            f.write(xml)

    def extract_info(self):
        """
        Extracts only the info of the source, does not download it
        """
        raise NotImplemented("Each source needs to implement how it extracts info")

    def post_process_entry(self, entry):
        if "tagging" in self.post_process:
            self._post_process_tagging(entry)

        # Move the file after all direct file modifications are complete
        output_file_path = _ffile(
            self.post_process["file_name"], self.output_path, entry, makedirs=True
        )
        copyfile(entry["file_path"], output_file_path)

        # Download the thumbnail if its present
        if "thumbnail_name" in self.post_process:
            thumbnail_dest_path = _ffile(
                self.post_process["thumbnail_name"],
                self.output_path,
                entry,
                makedirs=True,
            )
            if not os.path.isfile(thumbnail_dest_path):
                thumbnail_file_path = (
                    f"{self.WORKING_DIRECTORY}/{entry['id']}.{entry['thumbnail_ext']}"
                )
                if os.path.isfile(thumbnail_file_path):
                    copyfile(thumbnail_file_path, thumbnail_dest_path)

                if "convert_thumbnail" in self.post_process:
                    # TODO: Clean with yaml definitions
                    if self.post_process["convert_thumbnail"] == "jpg":
                        self.post_process["convert_thumbnail"] = "jpeg"
                    im = Image.open(thumbnail_dest_path).convert("RGB")
                    im.save(thumbnail_dest_path, self.post_process["convert_thumbnail"])

        if "nfo" in self.post_process:
            self._post_process_nfo(entry)

    @classmethod
    def from_dict(cls, name, d):
        # TODO: Make sure there is only one source, verify url
        if SubscriptionSource.SOUNDCLOUD in d:
            dclass = SoundcloudSubscription
        elif SubscriptionSource.YOUTUBE in d:
            dclass = YoutubeSubscription
        else:
            raise ValueError("dne")

        return dclass(
            name=name,
            options=d[dclass.source],
            ytdl_opts=d["ytdl_opts"],
            post_process=d["post_process"],
            overrides=d["overrides"],
            output_path=d["output_path"],
        )


class SoundcloudSubscription(Subscription):
    source = SubscriptionSource.SOUNDCLOUD

    def is_entry_skippable(self, entry):
        return self.options["skip_premiere_tracks"] and "/preview/" in entry["url"]

    def parse_entry(self, entry):
        entry = super(SoundcloudSubscription, self).parse_entry(entry)
        entry["upload_year"] = entry["upload_date"][:4]

        # Add thumbnail ext value
        entry["thumbnail_ext"] = entry["thumbnail"].split(".")[-1]

        # If the entry does not have album fields, set them to be the track fields
        if "album" not in entry:
            entry["album"] = entry["title"]
            entry["sanitized_album"] = entry["sanitized_title"]
            entry["album_year"] = entry["upload_year"]
            entry["tracknumber"] = 1
            entry["tracknumberpadded"] = f"{1:02d}"

        return entry

    def parse_album_entry(self, album_entry):
        album_year = min([int(e["upload_date"][:4]) for e in album_entry["entries"]])
        for track_number, e in enumerate(album_entry["entries"], start=1):
            e["album"] = album_entry["title"]
            e["sanitized_album"] = sanitize(album_entry["title"])
            e["album_year"] = album_year
            e["tracknumber"] = track_number
            e["tracknumberpadded"] = f"{track_number:02d}"
        return album_entry

    def extract_info(self):
        """
        Extracts only the info of the source, does not download it
        """
        base_url = f"https://soundcloud.com/{self.options['username']}"
        tracks = []

        if self.options.get("download_strategy") == "albums_then_tracks":
            track_ytdl_opts = {
                "download_archive": self.WORKING_DIRECTORY
                + "/ytdl-download-archive.txt",
                "forcejson": True,
            }
            # Get the album tracks first, but do not download. Unfortunately we cannot use download_archive for
            # this be
            with ytdl.YoutubeDL(self.ytdl_opts) as ytd:
                info = ytd.extract_info(base_url + "/albums", download=False)

            album_entries = [self.parse_album_entry(a) for a in info["entries"]]
            for album_entry in album_entries:
                tracks += [
                    self.parse_entry(e)
                    for e in album_entry["entries"]
                    if not self.is_entry_skippable(e)
                ]

            with ytdl.YoutubeDL(dict(self.ytdl_opts, **track_ytdl_opts)) as ytd:
                # Get the rest of the tracks that are part of the album tracks
                info = ytd.extract_info(base_url + "/tracks")
            album_track_ids = [t["id"] for t in tracks]
            tracks += [
                self.parse_entry(e)
                for e in info["entries"]
                if e["id"] not in album_track_ids and not self.is_entry_skippable(e)
            ]

            for e in tracks:
                self.post_process_entry(e)
        else:
            raise ValueError("Invalid download_strategy field for Soundcloud")


class YoutubeSubscription(Subscription):
    source = SubscriptionSource.YOUTUBE

    def parse_entry(self, entry):
        entry = super(YoutubeSubscription, self).parse_entry(entry)
        entry["upload_year"] = entry["upload_date"][:4]

        entry["thumbnail_ext"] = entry["thumbnail"].split(".")[-1]

        # Try to get the track, fall back on title
        entry["sanitized_track"] = sanitize(entry.get("track", entry["title"]))
        return entry

    def extract_info(self):
        playlist_id = self.options["playlist_id"]
        url = f"https://youtube.com/playlist?list={playlist_id}"
        track_ytdl_opts = {
            "download_archive": self.WORKING_DIRECTORY + "/ytdl-download-archive.txt",
            "writeinfojson": True,
        }

        # Do not get entries from the extract info, let it write to the info.json file and
        # load that instead. This is because if the video is already downloaded, it will
        # not fetch the metadata (maybe there is a way??)
        with ytdl.YoutubeDL(dict(self.ytdl_opts, **track_ytdl_opts)) as ytd:
            _ = ytd.extract_info(url)

        # Load the entries from info.json, ignore the playlist entry
        entries = []
        for file_name in os.listdir(self.WORKING_DIRECTORY):
            if file_name.endswith(".info.json") and not file_name.startswith(
                playlist_id
            ):
                with open(self.WORKING_DIRECTORY + "/" + file_name, "r") as f:
                    entries.append(json.load(f))

        entries = [self.parse_entry(e) for e in entries]
        for e in entries:
            self.post_process_entry(e)
