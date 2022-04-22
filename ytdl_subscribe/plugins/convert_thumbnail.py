import os

from PIL.Image import Image

from ytdl_subscribe.entries.entry import Entry
from ytdl_subscribe.plugins.plugin import Plugin
from ytdl_subscribe.plugins.plugin import PluginOptions
from ytdl_subscribe.validators.string_select_validator import StringSelectValidator


class ThumbnailTypes(StringSelectValidator):
    """Valid image types that thumbnails can be converted to"""

    _select_values = {"jpg"}


class ConvertThumbnailOptions(PluginOptions):
    _required_keys = {"to"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.convert_to = self._validate_key(key="to", validator=ThumbnailTypes)


class ConvertThumbnailPlugin(Plugin[ConvertThumbnailOptions]):
    plugin_options_type = ConvertThumbnailOptions

    def post_process_entry(self, entry: Entry):
        """
        Convert the source thumbnail to the desired type. Leave the original file name and
        extension intact to let output_options deal with renaming it.
        """
        if not os.path.isfile(entry.download_thumbnail_path):
            raise ValueError("Thumbnail not found")

        image = Image.open(entry.download_thumbnail_path).convert("RGB")

        # Pillow likes the formal 'jpeg' name and not 'jpg'
        thumbnail_format = self.plugin_options.convert_to.value
        if thumbnail_format == "jpg":
            thumbnail_format = "jpeg"

        image.save(fp=entry.download_thumbnail_path, format=thumbnail_format)
