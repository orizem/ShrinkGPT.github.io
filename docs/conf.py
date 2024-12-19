# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "Shrink.io"
copyright = "2024, Ori Tsemach, Eldar Garrett, Sahar Amar"
author = "Ori Tsemach, Eldar Garrett, Sahar Amar"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    # "myst_parser",
    # "sphinxcontrib.autojs",
    "sphinx_copybutton",
    "sphinx_autodoc_typehints",
    "sphinx_tabs.tabs",
    "sphinx_toolbox.collapse",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
# html_js_files = ["chat.js"]
html_logo = "_static/ShrinkGPT_logo.jpg"
html_favicon = "_static/ShrinkGPT_logo.ico"
html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "orizem",  # Username
    "github_repo": "ShrinkGPT.github.io",  # Repo name
    "github_version": "main",  # Version
    "conf_py_path": "/source/",  # Path in the checkout to the docs root
}

html_theme_options = {
    "logo": {
        "alt_text": "Shrink.io - Home",
        "text": "Shrink.io",
        "link": "https://shrink-io-19049486935.us-central1.run.app",
    },
    "use_edit_page_button": True,
    "icon_links": [
        {
            # Label for this link
            "name": "GitHub",
            # URL where the link will redirect
            "url": "https://github.com/orizem/ShrinkGPT.github.io",  # required
            # Icon class (if "type": "fontawesome"), or path to local image (if "type": "local")
            "icon": "fa-brands fa-square-github",
            # The type of image to be used (see below for details)
            "type": "fontawesome",
        }
    ],
}

# source_suffix = ['.rst', '.md']
