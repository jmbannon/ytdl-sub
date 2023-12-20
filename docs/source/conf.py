# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ytdl-sub"
copyright = "2023, Jesse Bannon"
author = "Jesse Bannon"
release = "2023.12.15"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    # "sphinx.ext.autosummary",
    "sphinx.ext.extlinks",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"

html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/jmbannon/ytdl-sub",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
        {
            "name": "Discord",
            "url": "https://discord.gg/v8j9RAHb4k",
            "icon": "https://img.shields.io/discord/994270357957648404?logo=Discord",
            "type": "url",
        },
    ],
    "announcement": (
        "Migration to <a href='https://ytdl-sub--841.org.readthedocs.build/en/841/config.html#beautifying-subscriptions'>beautiful subscriptions</a> is now live"
    ),
    "navigation_depth": 10,
    "show_toc_level": 10,
}

html_static_path = ["_static"]


# Make sure the all autosectionlabel targets are unique
autosectionlabel_prefix_document = True


extlinks = {"yt-dlp": ("https://github.com/yt-dlp/yt-dlp/%s", "yt-dlp%s")}

# -- Options for autodoc ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method.
autodoc_default_options = {
    "autodoc_typehints_format": "short",
    "autodoc_class_signature": "separated",
    "add_module_names": False,
    # "add_class_names": False,
}

python_use_unqualified_type_names = True
napoleon_numpy_docstring = True
napoleon_use_rtype = False
