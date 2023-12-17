# Configuration file for the Sphinx documentation builder.
#
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
        "Migration to <a href='~/build/index.html'>beautiful subscriptions</a> is now live"
    ),
}


html_static_path = ["_static"]
