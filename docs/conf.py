project = "FIREpyDAQ"
copyright = "Dushyant M. Chaudhari"
author = "Dushyant M. Chaudhari"
github_user = "ulfsri"
github_repo_name = "firepydaq"  # auto-detected from dirname if blank
github_version = "main"

extensions = [
    "sphinx-jsonschema",
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxext.opengraph",
    "sphinxcontrib.googleanalytics",
]
autoapi_dirs = ["../firepydaq"]  # location to parse for API reference
html_theme = "furo" #"sphinx_rtd_theme"
autoapi_options = [
    "members",
    'special-members',
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]

googleanalytics_id = "G-XXXXXXXXX"

ogp_site_url = "http://ulfsri.github.io/firepydaq"
ogp_image = "http://ulfsri.github.io/_images/FIREpyDAQDark.png"
ogp_description_length = 300
ogp_type = "website"

myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]
# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "README*",
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "jupyter_execute",
    "*venv*",
]

# for sphinx_rtd_theme
# html_context = {
#     "display_github": True,
#     "github_user": github_user,
#     # Auto-detect directory name.  This can break, but
#     # useful as a default.
#     "github_repo": github_repo_name, # or basename(dirname(realpath(__file__))),
#     "github_version": github_version,
#     "conf_py_path": "/docs/"
# }

html_theme_options = {
    "source_repository": "https://github.com/ulfsri/firepydaq/",
    "source_branch": "dev",
    "source_directory": "docs/",
    "top_of_page_buttons": ["view", "edit"],
}
