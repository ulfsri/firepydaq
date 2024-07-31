extensions = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
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
