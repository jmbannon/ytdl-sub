import inspect
from pathlib import Path
from typing import Dict
from typing import Type

from tools.docgen.docgen import DocGen
from tools.docgen.utils import get_function_docs
from tools.docgen.utils import properties
from tools.docgen.utils import section
from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.plugin.plugin_mapping import PluginMapping
from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.config.preset_options import YTDLOptions
from ytdl_sub.config.validators.options import OptionsValidator


def should_filter_property(property_name: str) -> bool:
    return property_name.startswith("_") or property_name in (
        "value",
        "source_variable_capture_dict",
        "dict",
        "keys",
        "dict_with_format_strings",
        "subscription_name",
        "list",
    )


def generate_plugin_docs(name: str, options: Type[OptionsValidator], offset: int) -> str:
    docs = ""
    docs += section(name, level=offset + 0)

    docs += inspect.cleandoc(options.__doc__)
    docs += "\n"

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
        }
        for plugin_name, plugin_type in PluginMapping._MAPPING.items():
            if plugin_name.startswith("_"):
                continue
            options_dict[plugin_name] = plugin_type.plugin_options_type

        docs = section("Plugins", level=0)
        for name in sorted(options_dict.keys()):
            docs += generate_plugin_docs(name, options_dict[name], offset=1)

        return docs
