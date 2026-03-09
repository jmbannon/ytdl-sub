from pathlib import Path
from typing import Dict
from typing import Set
from typing import Type

from tools.docgen.docgen import DocGen
from tools.docgen.utils import generate_options_validator_docs
from tools.docgen.utils import line_section
from tools.docgen.utils import section
from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.plugin.plugin_mapping import PluginMapping
from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.config.preset_options import YTDLOptions
from ytdl_sub.config.validators.options import OptionsValidator
from ytdl_sub.downloaders.url.validators import MultiUrlValidator

PLUGIN_NAMES_TO_SKIP_PROPERTIES: Set[str] = {
    "format",
    "match_filters",
    "music_tags",
    "filter_include",
    "filter_exclude",
    "embed_thumbnail",
    "square_thumbnail",
    "video_tags",
    "download",
}


class PluginsDocGen(DocGen):

    LOCATION = Path("docs/source/config_reference/plugins.rst")
    DOCSTRING_LOCATION = "The respective plugin files under src/ytdl_sub/plugins/"

    @classmethod
    def generate(cls):
        options_dict: Dict[str, Type[OptionsValidator]] = {
            "output_options": OutputOptions,
            "ytdl_options": YTDLOptions,
            "overrides": Overrides,
            "download": MultiUrlValidator,
        }
        for plugin_name, plugin_type in PluginMapping._MAPPING.items():
            if plugin_name.startswith("_"):
                continue
            options_dict[plugin_name] = plugin_type.plugin_options_type

        docs = section("Plugins", level=0)
        for idx, name in enumerate(sorted(options_dict.keys())):
            docs += line_section(section_idx=idx)
            docs += generate_options_validator_docs(
                name=name,
                options=options_dict[name],
                offset=1,
                skip_properties=name in PLUGIN_NAMES_TO_SKIP_PROPERTIES,
            )

        return docs
