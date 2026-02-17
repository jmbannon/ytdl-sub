from pathlib import Path

from tools.docgen.docgen import DocGen
from tools.docgen.utils import generate_options_validator_docs
from ytdl_sub.config.config_validator import ConfigOptions
from ytdl_sub.config.preset import Preset


class ConfigurationDocGen(DocGen):

    LOCATION = Path("docs/source/config_reference/config_yaml.rst")
    DOCSTRING_LOCATION = (
        "The respective function docstrings within ytdl_sub/config/config_validator.py"
    )

    @classmethod
    def generate(cls):
        docs = generate_options_validator_docs(
            name="Configuration File",
            options=ConfigOptions,
            offset=0,
            skip_properties=False,
            recurse_property_options=True,
            property_sections=True,
        )

        docs += generate_options_validator_docs(
            name="Presets",
            options=Preset,
            offset=0,
            skip_properties=False,
            recurse_property_options=False,
            property_sections=False
        )

        return docs
