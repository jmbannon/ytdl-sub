import inspect
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional
from typing import Type

from tools.docgen.docgen import DocGen
from tools.docgen.utils import line_section
from tools.docgen.utils import properties
from tools.docgen.utils import section
from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.plugin.plugin_mapping import PluginMapping
from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.config.preset_options import YTDLOptions
from ytdl_sub.config.validators.options import OptionsValidator
from ytdl_sub.downloaders.url.validators import MultiUrlValidator


def should_filter_all_properties(plugin_name: str) -> bool:
    return plugin_name in (
        "format",
        "match_filters",
        "music_tags",
        "filter_include",
        "filter_exclude",
        "embed_thumbnail",
        "video_tags",
        "download",
    )


def should_filter_property(property_name: str) -> bool:
    return property_name.startswith("_") or property_name in (
        "value",
        "source_variable_capture_dict",
        "dict",
        "keys",
        "dict_with_format_strings",
        "subscription_name",
        "list",
        "script",
        "unresolvable",
    )


def get_function_docs(function_name: str, obj: Any, level: int) -> str:
    docs = f"\n``{function_name}``\n\n"
    docs += inspect.cleandoc(getattr(obj, function_name).__doc__)
    docs += "\n\n"
    return docs


def generate_plugin_docs(name: str, options: Type[OptionsValidator], offset: int) -> str:
    docs = ""
    docs += section(name, level=offset + 0)

    docs += inspect.cleandoc(options.__doc__)
    docs += "\n"

    if should_filter_all_properties(name):
        return docs

    property_names = [prop for prop in properties(options) if not should_filter_property(prop)]
    for property_name in sorted(property_names):
        docs += get_function_docs(function_name=property_name, obj=options, level=offset + 1)

    return docs


class PluginsDocGen(DocGen):

    LOCATION = Path("docs/source/config_reference/plugins.rst")

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
            docs += generate_plugin_docs(name, options_dict[name], offset=1)

        return docs
