import inspect

from ytdl_sub.config.plugin.plugin_mapping import PluginMapping
from ytdl_sub.config.validators.options import OptionsValidator


def generate_docs(name: str, plugin_options: OptionsValidator):

    docs = ""
    docs += f"{name}\n{len(name) * '-'}\n"

    docs += inspect.cleandoc(plugin_options.__doc__)

    print(docs)


generate_docs(
    "output_directory_nfo_tags",
    PluginMapping._MAPPING["output_directory_nfo_tags"].plugin_options_type,
)
