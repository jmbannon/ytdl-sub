import os
from copy import deepcopy
from shutil import copyfile

import dicttoxml
import music_tag
from PIL import Image
from sanitize_filename import sanitize

from ytdl_subscribe.entries.entry import Entry


class Subscription(object):
    WORKING_DIRECTORY = ""

    def __init__(self, name, options, ytdl_opts, post_process, overrides, output_path):
        """
        Parameters
        ----------
        name: str
            Name of the subscription
        options: dict
            Dictionary of ytdl options, specific to the source type
        ytdl_opts: dict
            Dictionary of options passed directly to ytdl.
            See `youtube_dl.YoutubeDL.YoutubeDL` for options.
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
        for k, v in deepcopy(overrides).items():
            self.overrides[f"sanitized_{k}"] = sanitize(v)
        self.output_path = output_path

        # Separate each subscription's working directory
        self.WORKING_DIRECTORY += f"{'/' if self.WORKING_DIRECTORY else ''}{self.name}"

        # Always set outtmpl to the id and extension. Will be renamed using the subscription's output_path value
        self.ytdl_opts["outtmpl"] = self.WORKING_DIRECTORY + "/%(id)s.%(ext)s"
        self.ytdl_opts["writethumbnail"] = True

    def format_filepath(self, filepath_formatter: str, entry: Entry, makedirs=False):
        """
        Convert a filepath value in the config to an actual filepath.

        Parameters
        ----------
        filepath_formatter: str
            File path relative to the specified output path
        entry: Entry
            Entry used to populate any format variables in the filepath
        makedirs: bool
            Whether to create all directories in the final filepath.

        Returns
        -------
        str
            Full filepath.
        """
        file_name = entry.apply_formatter(filepath_formatter, overrides=self.overrides)
        output_file_path = f"{self.output_path}/{file_name}"
        if makedirs:
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        return output_file_path

    def _post_process_tagging(self, entry: Entry):
        t = music_tag.load_file(
            entry.file_path(relative_directory=self.WORKING_DIRECTORY)
        )
        for tag, tag_formatter in self.post_process["tagging"].items():
            t[tag] = entry.apply_formatter(tag_formatter, overrides=self.overrides)
        t.save()

    def _post_process_nfo(self, entry):
        nfo = {}
        for tag, tag_formatter in self.post_process["nfo"].items():
            nfo[tag] = entry.apply_formatter(tag_formatter, overrides=self.overrides)

        xml = dicttoxml.dicttoxml(
            obj=nfo,
            root="nfo_root" in self.post_process,
            custom_root=self.post_process.get("nfo_root"),
            attr_type=False,
        )
        nfo_file_path = self.format_filepath(
            self.post_process["nfo_name"], entry, makedirs=True
        )
        with open(nfo_file_path, "wb") as f:
            f.write(xml)

    def extract_info(self):
        """
        Extracts only the info of the source, does not download it
        """
        raise NotImplemented("Each source needs to implement how it extracts info")

    def post_process_entry(self, entry: Entry):
        if "tagging" in self.post_process:
            self._post_process_tagging(entry)

        # Move the file after all direct file modifications are complete
        output_file_path = self.format_filepath(
            self.post_process["file_name"], entry, makedirs=True
        )
        copyfile(
            entry.file_path(relative_directory=self.WORKING_DIRECTORY), output_file_path
        )

        # Download the thumbnail if its present
        if "thumbnail_name" in self.post_process:
            thumbnail_dest_path = self.format_filepath(
                self.post_process["thumbnail_name"],
                entry,
                makedirs=True,
            )
            if not os.path.isfile(thumbnail_dest_path):
                thumbnail_file_path = (
                    f"{self.WORKING_DIRECTORY}/{entry.uid}.{entry.thumbnail_ext}"
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
