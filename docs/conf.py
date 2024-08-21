project = "FIREpyDAQ"
copyright = "Dushyant M. Chaudhari"
author = "Dushyant M. Chaudhari"
github_user = "ulfsri"
github_repo_name = "firepydaq"  # auto-detected from dirname if blank
github_version = "main"

extensions = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    'sphinx.ext.autosectionlabel'
]
autoapi_dirs = ["../firepydaq"]  # location to parse for API reference
html_theme = "sphinx_rtd_theme"
autoapi_options = [
    "members",
    'special-members',
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]

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

html_context = {
    "display_github": True,
    "github_user": github_user,
    # Auto-detect directory name.  This can break, but
    # useful as a default.
    "github_repo": github_repo_name, # or basename(dirname(realpath(__file__))),
    "github_version": github_version,
    "conf_py_path": "/docs/"
}
