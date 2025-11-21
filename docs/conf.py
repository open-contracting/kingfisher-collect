# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "OCDS Kingfisher Collect"
copyright = "2019, Open Contracting Partnership"
author = "Open Contracting Partnership"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = []
html_theme_options = {
    "announcement": """
    <strong>New!</strong> Use the <a href="https://data.open-contracting.org/">OCP Data Registry</a> to
    <a href="https://data.open-contracting.org/">download OCDS data</a>, worldwide.
    """,
}

# -- Extension configuration -------------------------------------------------

autodoc_default_options = {
    "members": None,
    "member-order": "bysource",
}
autodoc_typehints = "description"

intersphinx_mapping = {
    "scrapy": ("https://docs.scrapy.org/en/latest/", None),
}
