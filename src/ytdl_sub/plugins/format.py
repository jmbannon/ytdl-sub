from typing import Dict
from typing import Optional

from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.validators.options import OptionsValidator
from ytdl_sub.validators.validators import StringValidator


class FormatOptions(OptionsValidator):
    """
    Set ``--format`` to pass into yt-dlp to download a specific format quality.
    Uses the same syntax as yt-dlp.

    Usage:

    .. code-block:: yaml

       format: "(bv*[height<=1080]+bestaudio/best[height<=1080])"
    """

    def __init__(self, name, value):
        super().__init__(name, value)
        self._format = StringValidator(name=name, value=value).value

    @property
    def format(self) -> str:
        """
        yt-dlp format, uses same syntax as yt-dlp.
        """
        return self._format


class FormatPlugin(Plugin[FormatOptions]):
    plugin_options_type = FormatOptions

    def ytdl_options(self) -> Optional[Dict]:
        """
        Returns
        -------
        yt-dlp format
        """
        return {"format": self.plugin_options.format}
