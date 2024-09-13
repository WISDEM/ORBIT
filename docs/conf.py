"""
Configuration file for the Sphinx documentation builder.

Jake Nunemaker
National Renewable Energy Lab
09/13/2019
"""

# -- Path setup --------------------------------------------------------------

import ORBIT

# -- Project information -----------------------------------------------------
project = "ORBIT"
copyright = "2020, National Renewable Energy Lab"  # noqa: A001
author = "Jake Nunemaker, Matt Shields, Rob Hammond"
release = ORBIT.__version__


# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
]

master_doc = "contents"
autodoc_member_order = "bysource"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = ["_themes"]

html_theme_options = {"display_version": True, "body_max_width": "70%"}

# Napoleon options
napoleon_google_docstring = False
napoleon_use_param = False
napoleon_use_ivar = True
